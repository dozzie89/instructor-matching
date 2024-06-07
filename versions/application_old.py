from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

import pandas as pd
import networkx as nx

#TODO: print all pairings of a department
#TODO: classes that they're matched on
#TODO: csv file of class blocks

#TODO: allow user input of specific times to block - unnecessary?
#TODO: prioritize pairing different departments
#TODO: allow user to select columns?
# GPGN, PHGN, HASS, EBGN, CS, materials

#initialize lists for taking in information
inst_bad = []
inst_good = []
df = None
instructors = None
output_df_download = None
pairs_download = None

def get_file():
    #read in file, perform data filtering
    try:
        global df
        file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        df = pd.read_excel(file_name)
    except Exception as e:
        lbl_print["text"] = f"{e}"
        raise(e)
    #lbl_print["text"] = f"{file_name} loaded successfully."
    lbl_print["text"] = "File loaded successfully."
    lbl_info["text"] = "Input class types/departments, then make pairs!"



def get_info():
    global df
    try:
        if input("Do you have any information you would like to submit? (y/n) ") != 'y': return df
        inp = int(input("\nWhat information do you have?\n 1. A pair of instructors that should not observe each other.\n 2. A pair of instructors that should observe each other.\n 3. An instructor would prefer a specific class to be observed.\n 4. An instructor has a time constraint outside of their listed classes.\n 5. No more information. (1/2/3/4/5) "))
    except Exception as e:
        print("Error with recieving input. Please try again.")
        get_info()
        return
    if inp not in range(1, 6):
        print("Invalid input. Please try again.")
        get_info()
        return
    elif inp == 5:
        print("Information recieved.")
        return
    elif inp == 1:
        insts = input("Which instructors should not observe each other? Please input two instructor IDs, separated by a space. Format: \'10001000 10001001\'\n").split(' ')
        inst_bad.append((insts[0], insts[1]))
        print("Input recieved.\n")
        get_info()
        return
    elif inp == 2:
        insts = input("Which instructors should observe each other? Please input two instructor IDs, separated by a space. Format: \'10001000 10001001\'\n").split(' ')
        inst_good.append((insts[0], insts[1]))
        print("Input recieved.\n")
        get_info()
        return
    elif inp == 3:
        inst = input("Which instructor has a specific class they would like observed? Please input the instructor ID. \n")

        print("This instructor teaches the following classes: \n")
        classes = df[df['PRIMARY_INSTRUCTOR_ID']==float(inst)]['CRN'].sort_values().unique()
        print(classes)

        crn = input("Which class would this instructor like observed? Please input the class CRN. \n")
        if float(crn) not in classes:
            print("Error with recieving input: invalid class. Please try again.")
            get_info()
            return
        
        df = df[(df['PRIMARY_INSTRUCTOR_ID'] != float(inst)) | (df['CRN'] == float(crn))]
        get_info()
        return
    elif inp == 4:
        #TODO
        inst = input("Which instructor has a time they are not available? Please input the instructor ID. \n")
        raise NotImplementedError()
        get_info()
        return
    else:
        print("Error with recieving input. Please try again.")
        get_info()
        return
    

def get_timeline(instructor):
    global df
    all_classes = []
    classes = df[df['PRIMARY_INSTRUCTOR_ID'] == instructor][['Begin Time', 'End Time', 'M', 'T', 'W', 'R', 'F']].values.tolist()
    for class_time in classes:
        for i in range(2, 7):
            s = class_time[i]
            if not pd.isnull(s):
                all_classes.append((class_time[0] + (2400 * (i - 2)), class_time[1] + (2400 * (i - 2))))
    return all_classes


def generate_edges():
    global df
    edges = set()
        
    inst_set = set()
    for (inst1, inst2) in inst_good:
        inst_set.add(float(inst1))
        inst_set.add(float(inst2))

    #TODO: make more efficient?
    #convert instructors, classes to edges in a graph
    for instruct_outer in instructors:
        if instruct_outer in inst_set: continue
        lbl_print["text"] = "Generating...{:.2f}%".format(100 * len(inst_set) / len(instructors))
        root.update()
        inst_set.add(instruct_outer)
        outer_timeline = get_timeline(instruct_outer)
        for instruct_inner in instructors:
            if instruct_inner in inst_set: continue
            if ((instruct_outer, instruct_inner) in inst_bad) or ((instruct_inner, instruct_outer) in inst_bad): continue
            inst_bool = True
            inner_timeline = get_timeline(instruct_inner)
            for class_outer in outer_timeline:
                if inst_bool == False: break
                for class_inner in inner_timeline:
                    if((class_outer[0] <= class_inner[0] and class_outer[1] >= class_inner[0]) or (class_outer[0] <= class_inner[1] and class_outer[1] >= class_inner[1])):
                        inst_bool = False
                        break
            if inst_bool == True:
                edges.add((instruct_outer, instruct_inner))

    lbl_print["text"] = "Successfully generated edges."
    return edges


def generate_graph(nodes, edges):
    try:
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        #if(input("Would you like a drawing of all possible pairings of these instructors? (y/n). ").lower() == 'y'):
            #nx.draw(G)
            #plt.savefig('output.png')
            #print("Successfully saved graph to output.png.")
    except Exception as e:
        lbl_info["text"] = "Error with graph process: {}".format(e)
        raise e

    #TODO: find better algorithm? this is a greedy algorithm, from what I can tell. implement hungarian maximum matching?
    try:
        pairs = nx.maximal_matching(G)
    except Exception as e:
        lbl_info["text"] = "Error with matching process: {}".format(e)
        raise e

    for (inst1, inst2) in inst_good:
        pairs.add((float(inst1), float(inst2)))

    lbl_print["text"] = "Successfully created pairs."
    return pairs


def get_name(id):
    global df
    return (df[df['PRIMARY_INSTRUCTOR_ID'] == id]['Primary Instr First Name'].values[0]) + " " + df[df['PRIMARY_INSTRUCTOR_ID'] == id]['Primary Instr Last Name'].values[0]


def output_pairs(pairs):
    global df
    global output_df_download
    global pairs_download
    data = [(
        get_name(pair[0]),
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[0]]['POSITION_TITLE'].values[0],
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[0]]['HOME_DEPARTMENT_DESC'].values[0],
        get_name(pair[1]),
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[1]]['POSITION_TITLE'].values[0],
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[1]]['HOME_DEPARTMENT_DESC'].values[0]
    ) for pair in pairs]
        
    pairs_download = pairs
    output_df_download = pd.DataFrame(data, columns=['inst1_name', 'inst1_role', 'inst1_dep', 'inst2_name', 'inst2_role', 'inst2_dep'], )

def info_helper_one():
    global df
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="A pair of instructors that should not observe each other.")
    helper_label.pack()

    checks = set()

    for id in df['PRIMARY_INSTRUCTOR_ID'].sort_values().unique():
        check = ttk.Checkbutton(t, text=id)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def info_one_manager_helper():
        global df
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
    global df
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="A pair of instructors that should observe each other.")
    helper_label.pack()

    checks = set()

    for id in df['PRIMARY_INSTRUCTOR_ID'].sort_values().unique():
        check = ttk.Checkbutton(t, text=id)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def info_two_manager_helper():
        global df
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
    global df
    t = Toplevel(root)
    helper_label = ttk.Label(master=t, text="Which instructor?")
    helper_label.pack()

    inst = StringVar()
    radios = set()

    for id in df['PRIMARY_INSTRUCTOR_ID'].sort_values().unique():
        radio = ttk.Radiobutton(t, text=id, variable=inst, value=id)
        radios.add(radio)
        radio.pack()

    def info_three_manager_helper():
        global df
        top = Toplevel(t)
        new_helper_label = ttk.Label(master=top, text="Which class?")
        new_helper_label.pack()

        inst_class = StringVar()
        class_radios = set()


        for crn in df[df['PRIMARY_INSTRUCTOR_ID'] == float(inst.get())]['CRN'].sort_values().unique():
            radio = ttk.Radiobutton(top, text=crn, variable=inst_class, value=crn)
            class_radios.add(radio)
            radio.pack()
            helper_label['text'] = inst.get()

        def info_three_manager_helper_helper():
            global df
            df = df[(df['PRIMARY_INSTRUCTOR_ID'] != float(inst.get())) | (df['CRN'] == float(inst_class.get()))]
            helper_label['text'] = 'Information recieved successfully. Submit a new instructor, or go back.'
            top.destroy()

        ttk.Button(master=top, text="Back", command=top.destroy).pack(side='left')
        ttk.Button(master=top, text="Submit", command=info_three_manager_helper_helper).pack(side='right')

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=info_three_manager_helper).pack(side='right')

def test_get_info():
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
    global instructors
    global df

    df = df[pd.notnull(df['PRIMARY_INSTRUCTOR_ID'])]
    instructors = set(df['PRIMARY_INSTRUCTOR_ID'].sort_values().unique())

    edges = generate_edges()
    pairs = generate_graph(instructors, edges)
    output_pairs(pairs)


def type_manager():
    global df

    t = Toplevel(root)
    ttk.Label(master=t, text="Which class types would you like to include?").pack()

    checks = set()

    for type in df['SCHEDULE_DESC'].sort_values().unique():
        check = ttk.Checkbutton(t, text=type)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def type_manager_helper():
        global df
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        df = df[df['SCHEDULE_DESC'].isin(true_set)]
        lbl_print['text'] = "Successfully recieved class types."
        t.destroy()
    
    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=type_manager_helper).pack(side='right')


def dep_manager():
    global df

    t = Toplevel(root)
    ttk.Label(master=t, text="Which departments would you like to include?").pack()

    checks = set()

    for dep in df['HOME_DEPARTMENT_DESC'].sort_values().unique():
    #for dep in df['Subj'].sort_values().unique():
        check = ttk.Checkbutton(t, text=dep)
        checks.add(check)
        check.pack()
        check.invoke()
        check.invoke()

    def dep_manager_helper():
        global df
        true_set = set()
        for check in checks:
            if check.instate(['selected']):
                true_set.add(check['text'])
        #df = df[df['Subj'].isin(true_set)]
        df = df[df['HOME_DEPARTMENT_DESC'].isin(true_set)]
        lbl_print['text'] = "Successfully recieved departments."
        t.destroy()

    ttk.Button(master=t, text="Back", command=t.destroy).pack(side='left')
    ttk.Button(master=t, text="Submit", command=dep_manager_helper).pack(side='right')

def download():
    global output_df_download
    global pairs_download
    #output_df.to_excel('output.xlsx', sheet_name='sheet1', index=False)
    #output_df.to_csv('output.csv', index=False)
    try:
        file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
        output_df_download.to_excel(file.name, sheet_name='sheet1', index=False)
    except Exception as e:
        lbl_print["text"] = "Error with downloading file: {}".format(e)
        raise e

    #lbl_print["text"] = "Successfully output pairs to \'output.xlsx\' and \'output.csv.\'"
    lbl_print["text"] = "Successfully downloaded file."

    #print unpaired instructors
    paired_instrs = set()
    for pair in pairs_download:
        paired_instrs.add(pair[0])
        paired_instrs.add(pair[1])
    diff = instructors - paired_instrs
    if diff: 
        text_var = "Unpaired Instructors: " + ' '.join([get_name(inst) for inst in diff])
    else:
        text_var = "Unpaired Instructors: None"
    lbl_info["text"] = text_var



root = Tk()
root.resizable(width=False, height=False)
root.title("Faculty Pairing")

lbl_print = ttk.Label(text="Starting process.")
lbl_print.pack(expand=True)

lbl_info = ttk.Label(text='Please select a file first (xlsx files only).')
lbl_info.pack()
ttk.Button(text="Select File", command=get_file).pack(fill='x')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

input_frame = ttk.Frame(root)
input_frame.pack()

ttk.Button(input_frame, text="Input Class Types", command=type_manager).pack(fill='x', side='left')
ttk.Button(input_frame, text="Input Departments", command=dep_manager).pack(fill='x', side='right')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

ttk.Button(text="Input Extra Info", command=test_get_info).pack(fill='x')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

ttk.Button(text="Generate Pairs", command=go_func).pack(fill='x')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

pairs_frame = ttk.Frame(root)
pairs_frame.pack()

ttk.Button(pairs_frame, text="Download Department", command=NotImplementedError).pack(fill='x', side='right')
ttk.Button(pairs_frame, text="Download Pairs", command=download).pack(fill='x', side='right')

ttk.Separator(root, orient=VERTICAL).pack(fill='x', expand=True)

ttk.Button(text="Quit", command=root.destroy).pack(fill='x')

root.mainloop()