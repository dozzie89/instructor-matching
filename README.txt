This application takes in 2 excel files (more information listed below) and outputs a pairing of faculty members based on their available times.


Usage:
If you would like a simple exe (mac only for now - sorry!), download match-macosx and run it.

Steps:
1. Download match-macosx, put it in a folder on your desktop
2. Open terminal (look up command prompt on mac)
3. Type the command "cd Desktop/{your_folder}" (without the brackets)
    - Note: if you'd rather leave the file in your downloads folder, you can. Just type "cd Downloads/" instead
4. Type the command "chmod +x ./match-macosx"
5. Run the exe by double clicking it in the folder, or run the command "./match-macosx"



The first file is a course scheduling file. It contains a list of every included instructor's preferred class or classes, along with relevant information for those classes.
Course Scheduling File:
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

The second file is a faculty nonavailability file. It contains a list of all "nonavailabilities," or times during the week instructors are unavailable outside of class.
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
