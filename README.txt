application.py takes in 2-3 excel files and outputs a pairing of faculty members based on their available times.

Usage:
python3 application.py



Necessary columns:

Course Scheduling File (list of instructors' preferred classes):
    Response ID
    Name
    Email
    Department
    Role
    Course_Dept
    Course_Number
    Course_Day_M
    Course_Day_T
    Course_Day_W
    Course_Day_R
    Course_Day_F
    Course_Begin_24
    Course_End_24
    Enrollment

    note: enrollment should be a categorical variable based on the number of buckets of different class sizes
    e.g. either "Under 30", "30-50", "Over 50". as long as it is categorical and consistent, it should work!

Faculty Scheduling File (extra availability info about faculty):
    Response ID
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Begin Time
    End Time

generate_test_data.py generates a class file and nonavailability file for a set of fake instructors.

Usage: 
python3 generate_test_data.py number_of_instructors average_number_of_nonavailabilites