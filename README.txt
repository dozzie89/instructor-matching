match.py takes in 2-3 excel files and outputs a pairing of faculty members based on their available times.

Usage:
python3 match.py



Necessary columns:

Course Scheduling File (list of instructors' preferred classes):
    Column Name         | Requirements
    --------------------|---------------------
    Response ID         | e.g. '123456789', must be consistent with the Response ID column in the other file
    Name                | e.g. 'John Smith'
    Email               | e.g. 'johnsmith@mines.edu'
    Department          | e.g. 'Computer Science'
    Role                | e.g. 'Associate Professor'
    Course_Dept         | e.g. 'CSCI'
    Course_Number       | e.g. '101'
    Course_Day_M        | e.g. 'M', must contain nothing if no class on that day, or 'M' if class is held on that day
    Course_Day_T        | e.g. 'T', see Course_Day_M
    Course_Day_W        | e.g. 'W', see Course_Day_M
    Course_Day_R        | e.g. 'R', see Course_Day_M
    Course_Day_F        | e.g. 'F', see Course_Day_M
    Course_Begin_24     | e.g. '1630', must be a four digit number representing the class start time in 24 hour
    Course_End_24       | e.g. '1730', must be a four digit number representing the class end time in 24 hour
    Enrollment          | e.g. '30-50', can be any value as long as it is consistent between classes. by default, only include three categories here.
    Course_Begin Time   | e.g. '1:00 PM'
    Course_End Time     | e.g. '2:00 PM'

Faculty Nonavailability File (extra availability info about faculty):
    Column Name         | Requirements
    --------------------|---------------------
    Response ID         | e.g. '123456789', must be consistent with the Response ID column in the other file
    Monday              | e.g. 'M', see Course_Day_M in other file
    Tuesday             | e.g. 'T', see Course_Day_M in other file
    Wednesday           | e.g. 'W', see Course_Day_M in other file
    Thursday            | e.g. 'R', see Course_Day_M in other file
    Friday              | e.g. 'F', see Course_Day_M in other file
    Begin Time          | e.g. '1630', must be a four digit number representing the class start in 24 hour time
    End Time            | e.g. '1730', must be a four digit number representing the class end in 24 hour time



Also included is a script for generating test data.
generate_test_data.py generates a class file and nonavailability file for a set of fake instructors.

Usage: 
python3 generate_test_data.py number_of_instructors average_number_of_nonavailabilites