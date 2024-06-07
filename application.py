from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

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
        df_classes = df_classes[pd.notnull(df_classes['Employee ID'])]
        df_classes = df_classes[pd.notnull(df_classes['Begin Time'])]
        df_classes = df_classes[pd.notnull(df_classes['End Time'])]
        df_classes = df_classes[df_classes['Not Participating'] == "Participating"]

        instructors = set(df_classes['Employee ID'].sort_values().unique())
    except Exception as e:
        raise(e)
    #lbl_print["text"] = f"{file_name} loaded successfully."
    lbl_print["text"] = "Class file loaded successfully."



def get_file_faculty():
    #read in faculty file, perform data filtering
    try:
        global df_classes
        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df_classes = pd.read_excel(file_name)
    except Exception as e:
        raise(e)
    #lbl_print["text"] = f"{file_name} loaded successfully."
    lbl_print["text"] = "Faculty file loaded successfully."



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
    


def get_timeline(instructor, conf):
    #convert instructor's availabilities into a list of times for graph matching
    global df_classes
    global df_scheduling
    all_classes = set()
    classes = df_classes[df_classes['Employee ID'] == instructor][['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F']].values.tolist()
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
    #convert instructors, classes to edges in a graph
    for instruct_outer in instructors:
        if instruct_outer in inst_set: continue
        #lbl_print["text"] = "Generating...{:.2f}%".format(100 * len(inst_set) / len(instructors))
        lbl_print["text"] = "Loading...number of possible matches generated: {:.2f}".format(len(edges))
        root.update()
        outer_timeline = get_timeline(instruct_outer, False)

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
                    edges.add((instruct_inner, instruct_outer))
                    break

            #if not any((c_inner[0] <= c_outer[1] and c_inner[1] >= c_outer[0]) for c_outer in outer_timeline for c_inner in inner_timeline):
                #edges.add((instruct_inner, instruct_outer))

    lbl_print["text"] = "Successfully generated edges."
    return edges


def generate_graph(nodes, edges):
    try:
        D = nx.DiGraph()
        D.add_nodes_from(nodes)
        D.add_edges_from(edges)

        G = D.to_undirected(reciprocal=True)
        #if(input("Would you like a drawing of all possible pairings of these instructors? (y/n). ").lower() == 'y'):
            #nx.draw(G)
            #plt.savefig('output.png')
            #print("Successfully saved graph to output.png.")
    except Exception as e:
        lbl_print["text"] = "Error with graph process: {}".format(e)
        raise e

    #TODO: find better algorithm? this is a greedy algorithm, from what I can tell. implement hungarian maximum matching?
    #TODO: weighted graph?
    try:
        #pairs = nx.maximal_matching(G)
        #outline taken from networkx maximal_matching function

        #sorted_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=False)

        def sort_func(edge):
            degree1 = G.degree(edge[0])
            degree2 = G.degree(edge[1])
            return degree1 + degree2

        sorted_edges = sorted(G.edges(), key=sort_func, reverse=False)

        pairs = set()
        nodes = set()

        same_dep = []
        diff_dep = []

        #TODO: bad.
        for edge in sorted_edges:
            u,v = edge
            if df_classes[df_classes['Employee ID'] == u]['Department'].values[0] == df_classes[df_classes['Employee ID'] == v]['Department'].values[0]:
                same_dep.append(edge)
            else:
                diff_dep.append(edge)
        for edge in diff_dep:
            u, v = edge
            if u not in nodes and v not in nodes and u != v:
                pairs.add(edge)
                nodes.update(edge)
        for edge in same_dep:
            u, v = edge
            if u not in nodes and v not in nodes and u != v:
                pairs.add(edge)
                nodes.update(edge)

    except Exception as e:
        lbl_print["text"] = "Error with matching process: {}".format(e)
        raise e

    for (inst1, inst2) in inst_good:
        pairs.add((float(inst1), float(inst2)))

    lbl_print["text"] = "Successfully created pairs."
    return pairs



def get_name(id):
    global df_classes
    return (df_classes[df_classes['Employee ID'] == id]['Full Name'].values[0])



def output_pairs(pairs):
    global df_classes
    global output_df_download
    global pairs_download

    df_class_output = df_classes[['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F', 'Employee ID', 'Subj', 'Crse', 'Bldg', 'Room']]

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
        df_classes[df_classes['Employee ID'] == pair[0]]['Department'].values[0],
        df_classes[df_classes['Employee ID'] == pair[0]]['Job Family'].values[0],
        df_classes[df_classes['Employee ID'] == pair[0]]['Full Title'].values[0],
        df_classes[df_classes['Employee ID'] == pair[0]]['Email - Primary Work or Primary Home'].values[0],
        [df_apply(time) for time in df_class_output[df_class_output['Employee ID'] == pair[0]].values.tolist()],

        pair[1],
        get_name(pair[1]),
        df_classes[df_classes['Employee ID'] == pair[1]]['Department'].values[0],
        df_classes[df_classes['Employee ID'] == pair[1]]['Job Family'].values[0],
        df_classes[df_classes['Employee ID'] == pair[1]]['Full Title'].values[0],
        df_classes[df_classes['Employee ID'] == pair[1]]['Email - Primary Work or Primary Home'].values[0],
        [df_apply(time) for time in df_class_output[df_class_output['Employee ID'] == pair[1]].values.tolist()],
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
            df_classes[df_classes['Employee ID'] == inst]['Department'].values[0], 
            df_classes[df_classes['Employee ID'] == inst]['Job Family'].values[0], 
            df_classes[df_classes['Employee ID'] == inst]['Full Title'].values[0],
            df_classes[df_classes['Employee ID'] == inst]['Email - Primary Work or Primary Home'].values[0],
            [df_apply(time) for time in df_class_output[df_class_output['Employee ID'] == inst].values.tolist()], 
            0, "Unpaired", 0, 0, 0, 0, 0))
    else:
        text_var = "Unpaired Instructors: None"
    lbl_print["text"] = text_var

    output_df_download = pd.DataFrame(data, columns=['inst1_id', 'inst1_name', 'inst1_dep', 'inst1_job', 'inst1_role', 'inst1_email', 'inst1_classes', 'inst2_id', 'inst2_name', 'inst2_dep', 'inst2_job', 'inst2_role', 'inst2_email', 'inst2_classes'], )



def info_helper_one():
    global instructors
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="A pair of instructors that should not observe each other.")
    helper_label.pack()

    checks = set()
    check_frame = Frame(t)
    check_frame.pack()

    for id in instructors:
        check = ttk.Checkbutton(check_frame, text=id)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def info_one_manager_helper():
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        if len(true_set) != 2:
            helper_label['text'] = "Invalid input recieved. Please try again."
            return
        inst_bad.append(tuple(true_set))
        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=info_one_manager_helper).pack(side='right')


def info_helper_two():
    global instructors
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="A pair of instructors that should observe each other.")
    helper_label.pack()

    checks = set()

    for id in instructors:
        check = ttk.Checkbutton(t, text=id)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def info_two_manager_helper():
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        if len(true_set) != 2:
            helper_label['text'] = "Invalid input recieved. Please try again."
            return
        inst_good.append(tuple(true_set))
        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=info_two_manager_helper).pack(side='right')


def info_helper_three():
    global instructors
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="Which instructor?")
    helper_label.pack()

    inst = StringVar()
    radios = set()

    for id in instructors:
        radio = ttk.Radiobutton(t, text=id, variable=inst, value=id)
        radios.add(radio)
        radio.pack()

    def info_three_manager_helper():
        global df_classes
        top = Toplevel(t)
        new_helper_label = ttk.Label(master=top, text="Which class?")
        new_helper_label.pack()

        inst_class = StringVar()
        class_radios = set()


        for crn in df_classes[df_classes['Employee ID'] == float(inst.get())]['CRN'].sort_values().unique():
            radio = ttk.Radiobutton(top, text=crn, variable=inst_class, value=crn)
            class_radios.add(radio)
            radio.pack()
            helper_label['text'] = inst.get()

        def info_three_manager_helper_helper():
            global df_classes
            df_classes = df_classes[(df_classes['Employee ID'] != float(inst.get())) | (df_classes['CRN'] == float(inst_class.get()))]
            helper_label['text'] = 'Information recieved successfully. Submit a new instructor, or go back.'
            top.destroy()

        ttk.Button(master=top, text="Back", command=top.destroy).pack(side='left')
        ttk.Button(master=top, text="Submit", command=info_three_manager_helper_helper).pack(side='right')

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=info_three_manager_helper).pack(side='right')


def get_info():
    if not check_func(): return
    
    t = Toplevel(root)
    ttk.Label(master=t, text="Is there any information you would like to provide?").pack()

    ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

    ttk.Button(master=t, text="A pair of instructors that should not observe each other.", command=info_helper_one).pack(fill='x')
    ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

    ttk.Button(master=t, text="A pair of instructors that should observe each other.", command=info_helper_two).pack(fill='x')
    ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

    ttk.Button(master=t, text="An instructor would prefer a specific class to be observed.", command=info_helper_three).pack(fill='x')
    ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

    ttk.Button(master=t, text="Back", command=t.destroy).pack(fill='x')



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
        instructors = set(df_classes['Employee ID'].sort_values().unique())
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
        df_classes = df_classes[df_classes['Employee ID'].isin(df_classes['Employee ID'].sort_values().unique())]
        instructors = set(df_classes['Employee ID'].sort_values().unique())
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
    global df_classes
    global df_scheduling

    if df_classes.empty:
        lbl_print['text'] = "Upload classes file first!"
        return False
    
    if df_classes.empty:
        lbl_print['text'] = "Upload faculty file first!"
        return False
    
    return True



root = Tk()
root.resizable(width=False, height=False)
root.title("Faculty Pairing")

lbl_print = ttk.Label(text="Please input files.")
lbl_print.pack(expand=True)

upload_frame = ttk.Frame(root)
upload_frame.pack()

ttk.Button(upload_frame, text="Select Class File", command=get_file_classes).pack(fill='x', side='left')
#ttk.Button(upload_frame, text="Select Faculty File", command=get_file_faculty).pack(fill='x', side='left')
ttk.Button(upload_frame, text="Select Scheduling File", command=get_file_scheduling).pack(fill='x', side='left')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

input_frame = ttk.Frame(root)
input_frame.pack()

ttk.Button(input_frame, text="Input Class Types", command=type_manager).pack(fill='x', side='left')
ttk.Button(input_frame, text="Input Departments", command=dep_manager).pack(side='left')
ttk.Button(input_frame, text="Input Extra Info", command=get_info).pack(side='left')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

pairs_frame = ttk.Frame(root)
pairs_frame.pack()

ttk.Button(pairs_frame, text="Generate Pairs", command=go_func).pack(fill='x', side='left')
ttk.Button(pairs_frame, text="Download Pairs", command=download).pack(side='left')
ttk.Button(pairs_frame, text="Download Department", command=download_dep).pack(side='left')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

ttk.Button(text="Quit", command=root.destroy).pack(fill='x')

root.mainloop()