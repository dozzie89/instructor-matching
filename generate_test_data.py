import pandas as pd
from tkinter.filedialog import asksaveasfile
from tkinter import *
import sys

import uuid
import random

from faker import Faker
fake = Faker()

NUMBER_OF_INSTRUCTORS = int(sys.argv[1])
NUMBER_OF_NONAVAILS = int(sys.argv[2]) * 2
inst_set = set()

print("Starting process.")

roles = ['Assistant Professor', 'Associate Professor', 'Professor', 'Teaching Assistant Professor', 'Teaching Associate Professor', 'Teaching Professor']
depts = ['EDNS', 'EEGN', 'MATH', 'MEGN', 'PEGN']
enrls = ['Fewer than 30', '30-50', 'More than 50']

def generate_rpid():
    rpid = uuid.uuid4()
    inst_set.add(rpid)
    return rpid

def generate_days():
    days = (None, None, None, None, None)
    rand = random.random()
    if rand <= 0.40:
        days = ('M', None, 'W', None, 'F')
    elif rand <= 0.8:
        days = (None, 'T', None, 'R', None)
    elif rand <= 0.84:
        days = ('M', None, None, None, None)
    elif rand <= 0.88:
        days = (None, 'T', None, None, None)
    elif rand <= 0.92:
        days = (None, None, 'W', None, None)
    elif rand <= 0.96:
        days = (None, None, None, 'R', None)
    else:
        days = (None, None, None, None, 'F')
    return days

def time12_to_time(start_time, end_time):
    if start_time > 1259:
        start_time -= 1200
        if(len(str(start_time)) > 3):
            start12 = str(start_time)[:2] + ":" + str(start_time)[-2:] + "PM"
        else:
            start12 = str(start_time)[:1] + ":" + str(start_time)[-2:] + "PM"
    else:
        if(len(str(start_time)) > 3):
            start12 = str(start_time)[:2] + ":" + str(start_time)[-2:] + "AM"
        else:
            start12 = str(start_time)[:1] + ":" + str(start_time)[-2:] + "AM"
    if end_time > 1259:
        end_time -= 1200
        if(len(str(end_time)) > 3):
            end12 = str(end_time)[:2] + ":" + str(end_time)[-2:] + "PM"
        else:
            end12 = str(end_time)[:1] + ":" + str(end_time)[-2:] + "PM"
    else:
        if(len(str(end_time)) > 3):
            end12 = str(end_time)[:2] + ":" + str(end_time)[-2:] + "AM"
        else:
            end12 = str(end_time)[:1] + ":" + str(end_time)[-2:] + "AM"
    return (start12, end12)

def generate_time():
    start_time = random.randint(8, 18) * 100
    start_time += random.choice([0, 30])
    end_time = start_time + random.choice([50, 75])
    if (end_time%100 >= 60):
        end_time = end_time + 40

    (start12, end12) = time12_to_time(start_time, end_time)
    return (start12, str(start_time), end12, str(end_time))

data = []

print("Starting generation loop.")

for iter in range(0, NUMBER_OF_INSTRUCTORS):
    rpid = generate_rpid()
    name = fake.name()
    mail = name.lower().replace(" ", "") + '@mines.edu'
    role = random.choice(roles)
    dept = random.choice(depts)
    numb = random.randint(100, 499)
    (day_m, day_t, day_w, day_r, day_f) = generate_days()
    (time_beg, time_beg24, time_end, time_end24) = generate_time()
    enrl = random.choice(enrls)

    data.append((rpid, name, mail, role, dept, numb, day_m, day_t, day_w, day_r, day_f, time_beg, time_beg24, time_end, time_end24, enrl))


print("Finished generation loop.")

output_df_download = pd.DataFrame(data, columns=['Response ID', 'Name', 'Email', 'Role', 'Course_Dept', 'Course_Number', 'Course_Day_M', 'Course_Day_T', 'Course_Day_W', 'Course_Day_R', 'Course_Day_F', 'Course_Begin Time', 'Course_Begin_24', 'Course_End Time', 'Course_End_24', 'Enrollment'], )

root = Tk()

try:
    file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
    output_df_download.to_excel(file.name, sheet_name='sheet1', index=False)
except Exception as e:
    raise e

root.destroy()

#GENERATE NONAVAILABILITIES:

nonavail_data = []

for rpid in inst_set:
    upper_bound = random.randint(0, NUMBER_OF_NONAVAILS)
    for nonavail in range(0, upper_bound):
        start_time = random.randint(6, 18) * 100
        start_time += random.randint(0, 59)
        end_time = start_time + random.randint(15, 300)
        if (end_time%100 >= 60):
            end_time = end_time + 40

        nonavail_data.append((rpid, random.choice(['M', None]), random.choice(['T', None]), random.choice(['W', None]), random.choice(['R', None]), random.choice(['F', None]), str(start_time), str(end_time)))

nonavail_df_download = pd.DataFrame(nonavail_data, columns=['Response ID', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Begin Time', 'End Time'], )


root = Tk()

try:
    file = asksaveasfile(defaultextension='.xlsx', filetypes=[("Excel files", '*.xlsx')])
    nonavail_df_download.to_excel(file.name, sheet_name='sheet1', index=False)
except Exception as e:
    raise e

root.destroy()