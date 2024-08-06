from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

import numpy as np
import pandas as pd
import networkx as nx

#TODO: re-match professors in bad pairs
# GPGN, PHGN, HASS, EBGN, CS, materials

#initialize lists for taking in information
inst_bad = []
inst_good = []

df_classes = pd.DataFrame()
df_scheduling = pd.DataFrame()

instructors = None
output_df_download = pd.DataFrame()
pairs_download = None



def get_file_classes():
    #read in class file, perform data filtering
    try:
        global df_classes
        global instructors

        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df_classes = pd.read_excel(file_name)
        df_classes = df_classes[pd.notnull(df_classes['Response ID'])]
        df_classes = df_classes[pd.notnull(df_classes['Begin Time'])]
        df_classes = df_classes[pd.notnull(df_classes['End Time'])]

        instructors = set(df_classes['Response ID'].sort_values().unique())
    except Exception as e:
        raise(e)
    #lbl_print["text"] = f"{file_name} loaded successfully."
    lbl_print["text"] = "Class file loaded successfully."



def get_file_scheduling():
    #read in schedule file, perform data filtering
    try:
        global df_scheduling
        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df_scheduling = pd.read_excel(file_name)
    except Exception as e:
        raise(e)
    #lbl_print["text"] = f"{file_name} loaded successfully."
    lbl_print["text"] = "Scheduling file loaded successfully."
    


def get_timeline(instructor, conf, class_code=None):
    #convert instructor's availabilities into a list of times for graph matching
    global df_classes
    global df_scheduling
    all_classes = set()
    if class_code:
        classes = df_classes[df_classes['Response ID'] == instructor][df_classes['CRN'] == class_code][['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F']].values.tolist()
    else:
        classes = df_classes[df_classes['Response ID'] == instructor][['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F']].values.tolist()
    if conf and not df_scheduling.empty:
        conflicts = df_scheduling[df_scheduling['PRIMARY_INSTRUCTOR_ID'] == instructor][['Begin Time', 'End Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].values.tolist()
        classes.extend(conflicts)
    for class_time in classes:
        for i in range(2, 7):
            s = class_time[i]
            if not pd.isnull(s):
                all_classes.add((class_time[0] + (2400 * (i - 2)), class_time[1] + (2400 * (i - 2))))
    return all_classes



def generate_edges():
    edges = set()
        
    inst_set = set()
    for (inst1, inst2) in inst_good:
        inst_set.add(float(inst1))
        inst_set.add(float(inst2))

    #TODO: make more efficient?
    #convert instructors, classes to edges in a graph by comparing classes with conflicts
    for instruct_outer in instructors:
        if instruct_outer in inst_set: continue
        #lbl_print["text"] = "Generating...{:.2f}%".format(100 * len(inst_set) / len(instructors))
        lbl_print["text"] = "Loading...number of possible matches generated: {:.2f}".format(len(edges))
        root.update()

        class_set = df_classes[df_classes['Response ID'] == instruct_outer][['CRN']].values.tolist()

        for outer_class in class_set:
            outer_timeline = get_timeline(instruct_outer, False, outer_class[0])

            for instruct_inner in instructors:
                if instruct_inner in inst_set or ((instruct_outer, instruct_inner) in inst_bad) or ((instruct_inner, instruct_outer) in inst_bad): continue
                inner_timeline = get_timeline(instruct_inner, True)

                c_add = True

                for o_class in outer_timeline:
                    for i_conflict in inner_timeline:
                        if not (i_conflict[0] >= o_class[1] or i_conflict[1] <= o_class[0]):
                            c_add = False
                            break
                    
                    if c_add: 
                        edges.add((instruct_inner, instruct_outer, outer_class[0]))
                        break

    #now we have one-way edges, so convert to two-way (checking both classes)
    final_edge_set = list()
    for edge in edges:
        u, v, class_code = edge
        #for each edge, find every edge with the reversed nodes and add to final list
        for (v_flip, u_flip, crn_flip) in [(n1, n2, crn) for (n1, n2, crn) in edges if (n1 == v and n2 == u)]:
            final_edge_set.append((u, v, class_code, crn_flip))

    lbl_print["text"] = "Successfully generated edges."
    return final_edge_set


def generate_graph(nodes, edges):

    #TODO: find better algorithm? this is a greedy algorithm, from what I can tell. implement hungarian maximum matching?
    #TODO: weighted graph?
    try:
        #pairs = nx.maximal_matching(G)
        #outline taken from networkx maximal_matching function

        pairs = set()
        nodes = set()

        same_dep = []
        diff_dep = []

        node_degrees = {}

        #TODO: bad.
        for edge in edges:
            u,v,u_class,v_class = edge

            if (u in node_degrees):
                node_degrees[u] += 1
            else:
                node_degrees.update({u: 1})
            if (v in node_degrees):
                node_degrees[v] += 1
            else:
                node_degrees.update({v: 1})

            if df_classes[df_classes['Response ID'] == u]['Department'].values[0] == df_classes[df_classes['Response ID'] == v]['Department'].values[0]:
                same_dep.append(edge)
            else:
                diff_dep.append(edge)

        #TODO: 3 or 4 buckets? what are the values?
        (low, high) = (30, 50)

        def class_size_check(edge):
            u,v,u_class,v_class = edge
            u_size = df_classes[df_classes['CRN'] == u_class]['Max Capacity'].values[0]
            v_size = df_classes[df_classes['CRN'] == v_class]['Max Capacity'].values[0]

            if u_size <= low:
                if v_size <= low:
                    return True
                else:
                    return False
            elif u_size <= high:
                if v_size > low and v_size <= high:
                    return True
                else:
                    return False
            else:
                if v_size > high:
                    return True
                else:
                    return False
            #return true if same class size
            #return false otherwise
            return

        edge_lists = [[], [], [], []]
        #0 = diff dep, same size
        #1 = diff dep, diff size
        #2 = same dep, same size
        #3 = same dep, diff size
        
        for edge in diff_dep:
            if class_size_check(edge):
                edge_lists[0].append(edge)
            else:
                edge_lists[1].append(edge)
        for edge in same_dep:
            if class_size_check(edge):
                edge_lists[2].append(edge)
            else:
                edge_lists[3].append(edge)
        
        def sort_func(edge):
            degree1 = node_degrees[edge[0]]
            degree2 = node_degrees[edge[1]]
            return degree1 + degree2

        for edge_list in edge_lists:
            edge_list = sorted(edge_list, key=sort_func, reverse=False)
            for edge in edge_list:
                u, v, u_class, u_size = edge
                if u not in nodes and v not in nodes and u != v:
                    pairs.add(edge)
                    nodes.add(u)
                    nodes.add(v)

    except Exception as e:
        lbl_print["text"] = "Error with matching process: {}".format(e)
        raise e

    #TODO: reimplement correctly
    #for (inst1, inst2) in inst_good:
    #    pairs.add((float(inst1), float(inst2)))

    lbl_print["text"] = "Successfully created pairs."
    return pairs



def get_name(id):
    global df_classes
    return (df_classes[df_classes['Response ID'] == id]['Name'].values[0])



def output_pairs(pairs):
    global df_classes
    global output_df_download
    global pairs_download

    df_class_output = df_classes[['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F', 'Response ID', 'Subj', 'Crse', 'Bldg', 'Room', 'CRN']]

    def df_apply(time):
        cls_str = time[8] + time[9] + ' '
        cls_str = cls_str + str(int(time[0])) + '-' + str(int(time[1])) + ' '
        for i in range(2, 7):
            if not pd.isna(time[i]):
                cls_str = cls_str + time[i]
        cls_str = cls_str + ' ' + time[10] + time[11]
        return cls_str
    
    data = [(
        pair[0],
        get_name(pair[0]),
        df_classes[df_classes['Response ID'] == pair[0]]['Department'].values[0],
        df_classes[df_classes['Response ID'] == pair[0]]['Role'].values[0],
        df_classes[df_classes['Response ID'] == pair[0]]['Email'].values[0],
        [df_apply(time) for time in df_class_output[df_class_output['Response ID'] == pair[0]][df_class_output['CRN'] == pair[3]].values.tolist()],

        pair[1],
        get_name(pair[1]),
        df_classes[df_classes['Response ID'] == pair[1]]['Department'].values[0],
        df_classes[df_classes['Response ID'] == pair[1]]['Role'].values[0],
        df_classes[df_classes['Response ID'] == pair[1]]['Email'].values[0],
        [df_apply(time) for time in df_class_output[df_class_output['Response ID'] == pair[1]][df_class_output['CRN'] == pair[2]].values.tolist()],
    ) for pair in pairs]
        
    pairs_download = pairs
    
    #print unpaired instructors
    paired_instrs = set()
    for pair in pairs_download:
        paired_instrs.add(pair[0])
        paired_instrs.add(pair[1])
    diff = instructors - paired_instrs
    if diff: 
        text_var = "Unpaired Instructors: " + ' '.join([get_name(inst) for inst in diff])
        for inst in diff:
            data.append((inst, get_name(inst), 
            df_classes[df_classes['Response ID'] == inst]['Department'].values[0], 
            df_classes[df_classes['Response ID'] == inst]['Role'].values[0], 
            df_classes[df_classes['Response ID'] == inst]['Email'].values[0],
            [df_apply(time) for time in df_class_output[df_class_output['Response ID'] == pair[1]][df_class_output['CRN'] == pair[2]].values.tolist()], 
            0, "Unpaired", 0, 0, 0, 0, 0))
    else:
        text_var = "Unpaired Instructors: None"
    lbl_print["text"] = text_var

    output_df_download = pd.DataFrame(data, columns=['inst1_id', 'inst1_name', 'inst1_dep', 'inst1_job', 'inst1_role', 'inst1_email', 'inst1_class', 'inst2_id', 'inst2_name', 'inst2_dep', 'inst2_job', 'inst2_role', 'inst2_email', 'inst2_class'], )



def go_func():
    if not check_func(): return
    global instructors

    edges = generate_edges()
    pairs = generate_graph(instructors, edges)
    output_pairs(pairs)



def type_manager():
    if not check_func(): return
    global df_classes

    t = Toplevel(root)
    ttk.Label(master=t, text="Which class types would you like to include?").pack()

    checks = set()

    for type in df_classes['SCHEDULE_DESC'].sort_values().unique():
        check = ttk.Checkbutton(t, text=type)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def type_manager_helper():
        global df_classes
        global instructors
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        df_classes = df_classes[df_classes['SCHEDULE_DESC'].isin(true_set)]
        instructors = set(df_classes['Response ID'].sort_values().unique())
        lbl_print['text'] = "Successfully recieved class types."
        t.destroy()
    
    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=type_manager_helper).pack(side='right')



def dep_manager():
    if not check_func(): return

    global df_classes
    global df_classes

    t = Toplevel(root)
    ttk.Label(master=t, text="Which departments would you like to include?").pack()

    checks = set()

    for dep in df_classes['Department'].sort_values().unique():
    #for dep in df['Subj'].sort_values().unique():
        check = ttk.Checkbutton(t, text=dep)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def dep_manager_helper():
        global df_classes
        global df_classes
        global instructors
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        #df = df[df['Subj'].isin(true_set)]
        df_classes = df_classes[df_classes['Department'].isin(true_set)]
        df_classes = df_classes[df_classes['Response ID'].isin(df_classes['Response ID'].sort_values().unique())]
        instructors = set(df_classes['Response ID'].sort_values().unique())
        lbl_print['text'] = "Successfully recieved departments."
        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=dep_manager_helper).pack(side='right')



def download():
    global output_df_download

    if output_df_download.empty:
        lbl_print['text'] = "Generate pairs first!"
        return
    #output_df.to_excel('output.xlsx', sheet_name='sheet1', index=False)
    #output_df.to_csv('output.csv', index=False)
    try:
        file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
        output_df_download.to_excel(file.name, sheet_name='sheet1', index=False)
        lbl_print['text'] = "Successfully downloaded file."
    except Exception as e:
        raise e


def download_dep():
    global output_df_download

    if output_df_download.empty:
        lbl_print['text'] = "Generate pairs first!"
        return
    
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="Which department would you like to download?")
    helper_label.pack()

    dep = StringVar()
    radios = set()

    for department in df_classes['Department'].sort_values().unique():
        radio = ttk.Radiobutton(t, text=department, variable=dep, value=department)
        radios.add(radio)
        radio.pack()

    def download_dep_helper():
        global output_df_download
        new_download = output_df_download[(output_df_download['inst1_dep'] == dep.get()) | (output_df_download['inst2_dep'] == dep.get())]
        
        try:
            file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
            new_download.to_excel(file.name, sheet_name='sheet1', index=False)
            lbl_print['text'] = "Successfully downloaded file."
        except Exception as e:
            raise e

        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Download", command=download_dep_helper).pack(side='right')



def check_func():
    global df_classes
    global df_scheduling

    if df_classes.empty:
        lbl_print['text'] = "Upload classes file first!"
        return False
    
    if df_scheduling.empty:
        lbl_print['text'] = "Upload faculty file first!"
        return False
    
    return True

def info_manager():
    type_manager()
    #TODO: select deps, class types, prof. types?

def download_manager():
    go_func()
    download()
    #TODO: generate pairs, download pairs (select departments)



root = Tk()
root.resizable(width=False, height=False)
root.title("Faculty Pairing")

lbl_print = ttk.Label(text="Please input files.")
lbl_print.pack(expand=True)

upload_frame = ttk.Frame(root)
upload_frame.pack()

ttk.Button(upload_frame, text="Select Class File", command=get_file_classes).pack(fill='x', side='left')
ttk.Button(upload_frame, text="Select Scheduling File", command=get_file_scheduling).pack(fill='x', side='left')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

input_frame = ttk.Frame(root)
input_frame.pack()

ttk.Button(input_frame, text="Select Information", command=info_manager).pack(fill='x', side='left')
#ttk.Button(input_frame, text="Input Class Types", command=type_manager).pack(fill='x', side='left')
#ttk.Button(input_frame, text="Input Departments", command=dep_manager).pack(side='left')
#ttk.Button(input_frame, text="Input Extra Info", command=get_info).pack(side='left')

#pairs_frame = ttk.Frame(root)
#pairs_frame.pack()
ttk.Button(input_frame, text="Generate/Download Pairs", command=download_manager).pack(side='left')
#ttk.Button(pairs_frame, text="Generate Pairs", command=go_func).pack(fill='x', side='left')
#ttk.Button(input_frame, text="Download Pairs", command=download).pack(side='left')
#ttk.Button(pairs_frame, text="Download Department", command=download_dep).pack(side='left')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

ttk.Button(text="Quit", command=root.destroy).pack(fill='x')

root.mainloop()