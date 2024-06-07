Takes in 2-3 excel files and outputs a pairing of faculty members based on their available times.

Usage:
python3 application.py



Necessary columns:

Course Scheduling File (list of instructors' classes):
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

Faculty Information File (extra information about faculty):
    Employee ID
    Full Title
    Job Family
    Department
    Full Name
    Email - Primary Work or Primary Home

Faculty Scheduling File (extra availability info about faculty):
    PRIMARY_INSTR_ID
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Begin Time
    End Time