from tkinter import Tk, StringVar, Toplevel
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

import pandas as pd
import networkx as nx

#extracted columns from class file
col_class_id = 'Response ID'
col_class_begin = 'Course_Begin_24'
col_class_end = 'Course_End_24'
col_class_m = 'Course_Day_M'
col_class_t = 'Course_Day_T'
col_class_w = 'Course_Day_W'
col_class_r = 'Course_Day_R'
col_class_f = 'Course_Day_F'
col_class_prof_dept = 'Department'
col_class_enrl = 'Enrollment'
col_class_role = 'Role'
col_class_email = 'Email'
col_class_name = 'Name'
col_class_class_dept = 'Course_Dept'
col_class_num = 'Course_Number'
col_class_beg12 = 'Course_Begin Time'
col_class_end12 = 'Course_End Time'

#extracted columns from scheduling file
col_schedule_id = 'Response ID'
col_schedule_begin = 'Begin Time'
col_schedule_end = 'End Time'
col_schedule_m = 'Monday'
col_schedule_t = 'Tuesday'
col_schedule_w = 'Wednesday'
col_schedule_r = 'Thursday'
col_schedule_f = 'Friday'

#initialize lists for taking in information
inst_bad = []
inst_good = []

df_classes = pd.DataFrame()
df_scheduling = pd.DataFrame()

instructors = None
output_df_download = pd.DataFrame()
pairs_download = None


import random

def get_file_classes():
    #read in class file, perform data filtering
    try:
        global df_classes
        global instructors

        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df_classes = pd.read_excel(file_name)
        df_classes = df_classes[pd.notnull(df_classes[col_class_id])]
        df_classes = df_classes[pd.notnull(df_classes[col_class_begin])]
        df_classes = df_classes[pd.notnull(df_classes[col_class_end])]

        temp = df_classes[col_class_id].sort_values().unique()
        random.shuffle(temp)

        instructors = set(temp)
    except Exception as e:
        raise(e)
    lbl_print["text"] = "Class file loaded successfully."



def get_file_scheduling():
    #read in schedule file, perform data filtering
    try:
        global df_scheduling
        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df_scheduling = pd.read_excel(file_name)
    except Exception as e:
        raise(e)
    lbl_print["text"] = "Scheduling file loaded successfully."
    


def get_timeline(instructor, conf):
    #convert instructor's nonavailabilities into a list of times for graph matching
    global df_classes
    global df_scheduling
    all_classes = set()
    classes = df_classes[df_classes[col_class_id] == instructor][[col_class_begin, col_class_end, col_class_m, col_class_t, col_class_w, col_class_r, col_class_f]].values.tolist()
    
    if conf and not df_scheduling.empty:
        conflicts = df_scheduling[df_scheduling[col_schedule_id] == instructor][[col_schedule_begin, col_schedule_end, col_schedule_m, col_schedule_t, col_schedule_w, col_schedule_r, col_schedule_f]].values.tolist()
        classes.extend(conflicts)
    for class_time in classes:
        for i in range(2, 7):
            s = class_time[i]
            if not pd.isnull(s):
                start = class_time[0] + (2400 * (i - 2))
                end = class_time[1] + (2400 * (i - 2))
                if (end - start) > 115:
                    end = start + 115
                all_classes.add((start, end))
    return all_classes



def generate_edges():
    edges = set()
        
    inst_set = set()
    for (inst1, inst2) in inst_good:
        inst_set.add(float(inst1))
        inst_set.add(float(inst2))

    #convert instructors, classes to edges in a graph by comparing classes with conflicts
    for instruct_outer in instructors:
        if instruct_outer in inst_set: continue
        lbl_print["text"] = f"Loading...number of possible matches generated: {len(edges)}. Maximum possible matches: {len(df_classes) ** 2}."
        root.update()

        outer_timeline = get_timeline(instruct_outer, False)

        for instruct_inner in instructors:
            if instruct_inner in inst_set or ((instruct_outer, instruct_inner) in inst_bad) or ((instruct_inner, instruct_outer) in inst_bad): continue
            inner_timeline = get_timeline(instruct_inner, True)


            for o_class in outer_timeline:
                c_add = True
                for i_conflict in inner_timeline:
                    if not (i_conflict[0] >= o_class[1] or i_conflict[1] <= o_class[0]):
                        c_add = False
                        break
                
                if c_add: 
                    edges.add((instruct_inner, instruct_outer))

    lbl_print["text"] = "Successfully generated edges."
    return edges


def generate_graph(nodes, edges):
    # convert generated nodes/edges into a networkx digraph for matching algorithm
    try:
        D = nx.DiGraph()
        D.add_nodes_from(nodes)
        D.add_edges_from(edges)

        G = D.to_undirected(reciprocal=True)
    except Exception as e:
        lbl_print["text"] = "Error with graph process: {}".format(e)
        raise e

    try:
        #outline taken from networkx maximal_matching function

        pairs = set()
        nodes = set()

        same_dep = []
        diff_dep = []

        for edge in G.edges:
            u,v = edge

            if df_classes[df_classes[col_class_id] == u][col_class_class_dept].values[0] == df_classes[df_classes[col_class_id] == v][col_class_class_dept].values[0]:
                same_dep.append(edge)
            else:
                diff_dep.append(edge)

        def class_size_check(edge):
            u,v = edge
            u_size = df_classes[df_classes[col_class_id] == u][col_class_enrl].values[0]
            v_size = df_classes[df_classes[col_class_id] == v][col_class_enrl].values[0]

            return u_size == v_size
            #returns true if same class size
            #returns false otherwise

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
            u,v = edge
            if (u not in G.nodes) or (v not in G.nodes):
                return 100000000
            degree1 = G.degree[u]
            degree2 = G.degree[v]
            if (degree1 == 1) or (degree2 == 1):
                return 1
            return (degree1 + degree2)

        #prioritize instructors in different departments, then instructors with matching class sizes
        for edge_list in edge_lists:
            edge_list = sorted(edge_list, key=sort_func, reverse=False)
            for edge in edge_list:
                u, v = edge
                if u not in nodes and v not in nodes and u != v:
                    pairs.add(edge)
                    nodes.add(u)
                    nodes.add(v)

        test_pairs = set()
        test_nodes = set()
        if (len(pairs) * 2) < (len(instructors) - 1):
            edge_list = sorted(G.edges, key=sort_func, reverse=False)
            for edge in edge_list:
                u, v = edge
                if u not in test_nodes and v not in test_nodes and u != v:
                    test_pairs.add(edge)
                    test_nodes.add(u)
                    test_nodes.add(v)
                    G.remove_node(u)
                    G.remove_node(v)
                    edge_list = sorted(edge_list, key=sort_func, reverse=False)
            print(len(pairs) * 2)
            if (len(test_pairs) * 2) >= (len(instructors) - 1):
                pairs = test_pairs
                nodes = test_nodes


    except Exception as e:
        lbl_print["text"] = "Error with matching process: {}".format(e)
        raise e

    lbl_print["text"] = "Successfully created pairs."
    return pairs



def get_name(id):
    global df_classes
    return (df_classes[df_classes[col_class_id] == id][col_class_name].values[0])


# convert generated pairs to a pandas dataframe with relevant information (including unmatched instructors)
def output_pairs(pairs):
    global df_classes
    global output_df_download
    global pairs_download

    df_class_output = df_classes[[col_class_beg12, col_class_end12, col_class_m, col_class_t, col_class_w, col_class_r, col_class_f, col_class_id, col_class_class_dept, col_class_num]]

    def df_apply(time):
        cls_str = time[8] + str(time[9]) + ' '
        cls_str = cls_str + time[0] + '-' + time[1] + ' '
        for i in range(2, 7):
            if not pd.isna(time[i]):
                cls_str = cls_str + time[i]
        return cls_str
    
    data = [(
        get_name(pair[0]),
        df_classes[df_classes[col_class_id] == pair[0]][col_class_class_dept].values[0],
        df_classes[df_classes[col_class_id] == pair[0]][col_class_role].values[0],
        df_classes[df_classes[col_class_id] == pair[0]][col_class_email].values[0],
        [df_apply(time) for time in df_class_output[df_class_output[col_class_id] == pair[0]].values.tolist()],
        df_classes[df_classes[col_class_id] == pair[0]][col_class_enrl].values[0],

        get_name(pair[1]),
        df_classes[df_classes[col_class_id] == pair[1]][col_class_class_dept].values[0],
        df_classes[df_classes[col_class_id] == pair[1]][col_class_role].values[0],
        df_classes[df_classes[col_class_id] == pair[1]][col_class_email].values[0],
        [df_apply(time) for time in df_class_output[df_class_output[col_class_id] == pair[1]].values.tolist()],
        df_classes[df_classes[col_class_id] == pair[1]][col_class_enrl].values[0],
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
            data.append((get_name(inst), 
            df_classes[df_classes[col_class_id] == inst][col_class_class_dept].values[0], 
            df_classes[df_classes[col_class_id] == inst][col_class_role].values[0], 
            df_classes[df_classes[col_class_id] == inst][col_class_email].values[0],
            [df_apply(time) for time in df_class_output[df_class_output[col_class_id] == inst].values.tolist()], 
            df_classes[df_classes[col_class_id] == inst][col_class_enrl].values[0],
            "Unpaired", None, None, None, None, None))
    else:
        text_var = "Unpaired Instructors: None"
    lbl_print["text"] = text_var

    output_df_download = pd.DataFrame(data, columns=['inst1_name', 'inst1_dep', 'inst1_job', 'inst1_email', 'inst1_class', 'inst1_enroll', 'inst2_name', 'inst2_dep', 'inst2_job', 'inst2_email', 'inst2_class', 'inst2_enroll'], )



def go_func():
    if not check_func(): return
    global instructors

    edges = generate_edges()
    pairs = generate_graph(instructors, edges)
    output_pairs(pairs)


# tkinter department menu helper function
def dep_manager():
    if not check_func(): return

    global df_classes
    global df_classes

    t = Toplevel(root)
    ttk.Label(master=t, text="Which departments would you like to include?").pack()

    checks = set()

    for dep in df_classes[col_class_class_dept].sort_values().unique():
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
        df_classes = df_classes[df_classes[col_class_class_dept].isin(true_set)]
        df_classes = df_classes[df_classes[col_class_id].isin(df_classes[col_class_id].sort_values().unique())]
        instructors = set(df_classes[col_class_id].sort_values().unique())
        lbl_print['text'] = "Successfully recieved departments."
        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=dep_manager_helper).pack(side='right')


#tkinter download menu helper function
def download():
    global output_df_download

    if output_df_download.empty:
        lbl_print['text'] = "Generate pairs first!"
        return
    try:
        file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
        output_df_download.to_excel(file.name, sheet_name='sheet1', index=False)
        lbl_print['text'] = "Successfully downloaded file."
    except Exception as e:
        raise e


#only allow the user to download pairs if correct files have been submitted
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


def download_manager():
    go_func()
    download()


#tkinter setup
root = Tk()
root.resizable(width=False, height=False)
root.title("Faculty Pairing")

lbl_print = ttk.Label(text="Please input files.")
lbl_print.pack(expand=True)

upload_frame = ttk.Frame(root)
upload_frame.pack()

ttk.Button(upload_frame, text="Select Course Scheduling File", command=get_file_classes).pack(fill='x', side='left')
ttk.Button(upload_frame, text="Select Faculty Nonavailability File", command=get_file_scheduling).pack(fill='x', side='left')

ttk.Separator(root, orient='vertical').pack(fill='x', expand=True)

input_frame = ttk.Frame(root)
input_frame.pack()

ttk.Button(input_frame, text="Select Included Departments", command=dep_manager).pack(fill='x', side='left')

ttk.Button(input_frame, text="Generate/Download Pairs", command=download_manager).pack(side='left')

ttk.Separator(root, orient='vertical').pack(fill='x', expand=True)

ttk.Button(text="Quit", command=root.destroy).pack(fill='x')

root.mainloop()