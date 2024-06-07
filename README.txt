Takes in an excel file and outputs a pairing of faculty members based on their available times.

Usage:
python3 application.py

Necessary columns:

Course Scheduling File:
Not Participating
PRIMARY_INSTR_ID
CRN
Begin Time
End Time
M
T
W
R
F
SCHEDULE_DESC
Subj
Crse
Bldg
Room

Faculty Information File (or combined w/ classes):
Employee ID
Full Title
Job Family
Department
Full Name
Email - Primary Work or Primary Home

Faculty Scheduling File:
PRIMARY_INSTR_ID
Monday
Tuesday
Wednesday
Thursday
Friday
Begin Time
End Time