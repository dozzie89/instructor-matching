from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
import pandas as pd
import numpy as np

file_name = askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
df_classes = pd.read_excel(file_name)
df_classes = df_classes[pd.notnull(df_classes['Employee ID'])]
df_classes = df_classes[pd.notnull(df_classes['Begin Time'])]
df_classes = df_classes[pd.notnull(df_classes['End Time'])]
df_classes = df_classes[df_classes['Not Participating'] == "Participating"]

class_sizes = list(df_classes["Max Capacity"])

high, middle, low = np.percentile(class_sizes, [75, 50, 25])
#high, middle = (45, 15)

conditions = [
    (df_classes['Max Capacity'] <= middle),
    (df_classes['Max Capacity'] > middle) & (df_classes['Max Capacity'] <= high),
    (df_classes['Max Capacity'] > high)
    ]

df_classes['capacity_tier'] = np.select(conditions, ['0', '1', '2'])

print(df_classes[['Max Capacity', 'capacity_tier']].head())
print(high, middle, low)

class_sizes.sort()
print(class_sizes)