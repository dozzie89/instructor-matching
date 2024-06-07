from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import sys

import pandas as pd
import networkx as nx

#TODO: allow user to select columns?
#TODO: role, dep
# print all pairings of a department
# GPGN, PHGN, HASS, EBGN
# For matching, does the observing instructor have to be available for all days of the class they are observing?

#initialize lists for taking in information
inst_bad = []
inst_good = []
df = None
instructors = None

def get_file():
    #TODO: make work
    #read in file, perform data filtering
    try:
        global df
        df = pd.read_excel(sys.argv[1])
    except Exception as e:
        print(e)
        raise(e)
    print("File {} loaded successfully.".format(sys.argv[1]))



def filter_df():
    global df
    df = df[pd.notnull(df['PRIMARY_INSTRUCTOR_ID'])]

    #take in class types
    try:
        #if you just push enter, include just lecture
        inp = input("What class types would you like to include? Please write the names as listed in the Excel file and format as follows: \"Lecture Research ...\"\n")
        if inp:
            df = df[df['SCHEDULE_DESC'].isin(inp.split(' '))]
        else:
            df = df[df['SCHEDULE_DESC']=='Lecture']
    except Exception as e:
        print("Error in listing class types:")
        raise(e)

    #TODO: use home department?
    #take in departments
    try:
        #if you just push enter, include all departments
        deps = input("What departments would you like to include? Please write the four letter codes and format as follows: \"DEP1 DEP2 DEP3 ...\"\n")
        if deps:
            df = df[df['Subj'].isin(deps.split(' '))]
        deps = deps.split(' ')
    except Exception as e:
        print("Error in listing departments:")
        raise(e)
    
    #TODO: filtering? don't need?
    #df = df[['CRN', 'Subj', 'Short Title', 'M', 'T', 'W', 'R', 'F', 'S', 'U', 'Begin Time', 'End Time', 'Bldg', 'Room', 'Primary Instr First Name', 'Primary Instr Last Name', 'PRIMARY_INSTRUCTOR_ID']]


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
    print("Generating edges... (warning: this might take a little while, depending on how many instructors you want to pair)")
        
    inst_set = set()
    for (inst1, inst2) in inst_good:
        inst_set.add(float(inst1))
        inst_set.add(float(inst2))

    #TODO: make more efficient?
    #convert instructors, classes to edges in a graph
    for instruct_outer in instructors:
        if instruct_outer in inst_set: continue
        print("Generating...{:.2f}%".format(100 * len(inst_set) / len(instructors)))
        inst_set.add(instruct_outer)
        #print("Checking outer Prof. {}".format(instruct_outer))
        outer_timeline = get_timeline(instruct_outer)
        for instruct_inner in instructors:
            if instruct_inner in inst_set: continue
            if ((instruct_outer, instruct_inner) in inst_bad) or ((instruct_inner, instruct_outer) in inst_bad): continue
            inst_bool = True
            #print("   Checking inner Prof. {}".format(instruct_inner))
            inner_timeline = get_timeline(instruct_inner)
            for class_outer in outer_timeline:
                if inst_bool == False: break
                for class_inner in inner_timeline:
                    #print("Outer class: {} || Inner class: {}".format(class_outer, class_inner))
                    if((class_outer[0] <= class_inner[0] and class_outer[1] >= class_inner[0]) or (class_outer[0] <= class_inner[1] and class_outer[1] >= class_inner[1])):
                        inst_bool = False
                        break
            if inst_bool == True:
                edges.add((instruct_outer, instruct_inner))

    print("Successfully generated edges.\n")
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
        print("Error with graph process.")
        raise e

    #TODO: find better algorithm? this is a greedy algorithm, from what I can tell. implement hungarian maximum matching?
    try:
        pairs = nx.maximal_matching(G)
    except Exception as e:
        print("Error with matching process.")
        raise e

    for (inst1, inst2) in inst_good:
        pairs.add((float(inst1), float(inst2)))

    print("Successfully created pairs.")
    return pairs



def get_name(id):
    return (df[df['PRIMARY_INSTRUCTOR_ID'] == id]['Primary Instr First Name'].values[0]) + " " + df[df['PRIMARY_INSTRUCTOR_ID'] == id]['Primary Instr Last Name'].values[0]



def output_pairs(pairs):
    #TODO: better output - departments, classes, etc.
    data = [(
        get_name(pair[0]),
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[0]]['POSITION_TITLE'].values[0],
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[0]]['HOME_DEPARTMENT_DESC'].values[0],
        get_name(pair[1]),
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[1]]['POSITION_TITLE'].values[0],
        df[df['PRIMARY_INSTRUCTOR_ID'] == pair[1]]['HOME_DEPARTMENT_DESC'].values[0]
    ) for pair in pairs]

    output_df = pd.DataFrame(data, columns=['inst1_name', 'inst1_role', 'inst1_dep', 'inst2_name', 'inst2_role', 'inst2_dep'], )
    output_df.to_excel('output.xlsx', sheet_name='sheet1', index=False)
    # can remove - just for ease of observing results
    output_df.to_csv('output.csv', index=False)

    print("Successfully output pairs to \'output.xlsx\' and \'output.csv.\'\n")

    #print unpaired instructors
    paired_instrs = set()
    for pair in pairs:
        paired_instrs.add(pair[0])
        paired_instrs.add(pair[1])
    diff = instructors - paired_instrs
    prnt = 'None'
    if diff: prnt = diff
    print("Unpaired Instructors: ", [get_name(inst) for inst in prnt])

    print("Process complete.")



#TODO: take input about any changes

print("Starting process.")

get_file()

filter_df()
get_info()

instructors = set(df['PRIMARY_INSTRUCTOR_ID'].sort_values().unique())

edges = generate_edges()
pairs = generate_graph(instructors, edges)
output_pairs(pairs)