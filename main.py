# importing required modules
import os
import re
import PyPDF2
from termcolor import colored
from tqdm import tqdm
import sqlite3

PDF_FILE_NAME = "MA2022 GAZETTE.pdf"
DB_FILE_NAME = f'{PDF_FILE_NAME}.db'

def create_text_file():

    json_data = {}

    # creating a pdf file object
    pdfFileObj = open('MA2022 GAZETTE.pdf', 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    number_of_pages = pdfReader.numPages

    student_result_pattern = "[0-9]{6} +[A-Z ]+[-]* [A-Z0-9,]*"
    student_result_split_pattern = "([0-9]{6})([A-Z\s]*)([-]*)"
    institute_name_pattern = "[0-9]{6}-[A-Z., ()-]*"


    print(colored("EXTRACTING TEXT FROM PDF ..........", "green"))

    institute_code = None
    institute_name = None

    # Initializing database
    sql = sqlite3.connect(DB_FILE_NAME)
    cursor = sql.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS result(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, roll_num INTEGER, marks INTEGER, institute INETEGER, institute_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS schools(id INTEGER PRIMARY KEY AUTOINCREMENT, school_code INTEGER, school_name)")

    for i in tqdm(range(number_of_pages)):
        pageObj = pdfReader.getPage(i)
        page_text = pageObj.extractText()

        # creating lines list
        page_text_lines = page_text.split("\n")

        for i, line in enumerate(page_text_lines):
            line = line.strip()
            if re.match(student_result_pattern, line):
                # when i == 41 then two students numbers are in one line
                if i == 41:
                    # seperating students
                    two_students = re.findall(student_result_pattern, line)
                    for student in two_students:
                        # saving into database
                        result = re.split(student_result_split_pattern, student)
                        try:
                            marks = int(result[4])
                        except:
                            pass
                        cursor.execute("INSERT INTO result(name, roll_num, marks, institute, institute_name) VALUES(?,?,?,?,?)", 
                        (result[2], result[1], marks, int(institute_code), institute_name))
                else:
                    # Saving into database
                    result = re.split(student_result_split_pattern, line)
                    marks = -1
                    try:
                        marks = int(result[4])
                    except:
                        pass
                        
                    cursor.execute("INSERT INTO result(name, roll_num, marks, institute, institute_name) VALUES(?,?,?,?,?)", 
                    (result[2], result[1], marks, institute_code, institute_name))
                    
            elif re.match(institute_name_pattern, line):
                position = line.find("-")
                institute_code = int(line[:position])
                institute_name = line[position+1:]
                cursor.execute("INSERT INTO schools(school_code, school_name) VALUES(?,?)",(institute_code, institute_name))            

    # Commiting changes in database 
    sql.commit()
    cursor.close()
    sql.close()

    # closing the pdf file object
    pdfFileObj.close()


if __name__ == '__main__':
    if not os.path.isfile(DB_FILE_NAME):
        create_text_file()
