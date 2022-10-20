# importing required modules
import os
import re
import PyPDF2
from termcolor import colored
from tqdm import tqdm
import sqlite3

# -------------------- Global Variables ---------------------

PDF_FILE_PATH = '/home/hammad/Downloads/GazetteInterAnnual2022.pdf'
DB_FILE_PATH = None
DB_FOLDER_NAME = "EXTRACTED DATA"

# -----------------------------------------------------------

def extract_data_from_pdf():

    json_data = {}

    # creating a pdf file object
    pdfFileObj = open(PDF_FILE_PATH, 'rb')

    # creating a pdf reader object
    try:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    except:
        print(colored(f"'{PDF_FILE_PATH}' FILE READING ERROR. PLEASE CHECK FILE", "red"))
        exit()
    number_of_pages = pdfReader.numPages

    student_result_pattern = "[0-9]{6} +[A-Z ]+[-]* [A-Z0-9,]*"
    student_result_split_pattern = "([0-9]{6})([A-Z\s]*)([-]*)"
    institute_name_pattern = "[0-9]{6}-[A-Z., ()-]*"


    print(colored("EXTRACTING TEXT FROM PDF ..........", "green"))

    institute_code = None
    institute_name = None

    # Initializing database
    sql = sqlite3.connect(DB_FILE_PATH)
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

def get_pdf_file_path():
    # Getting file path from user
    print("( -- Enter path of gazzete pdf you downloaded from " + colored("https://bisegrw.edu.pk", "blue") + " -- )\n")
    while True:
        PDF_FILE_PATH = input("File Path: ")
        print("\n")
        # Filtering path
        PDF_FILE_PATH = PDF_FILE_PATH.replace("'", "")
        PDF_FILE_PATH = PDF_FILE_PATH.replace("\"", "")
        PDF_FILE_PATH = PDF_FILE_PATH.replace("\\", "/")
        if os.path.isfile(PDF_FILE_PATH):
            break
        else:
            print(colored(f"'{DB_FILE_PATH}' file not found."))

    


if __name__ == '__main__':

    # If file path is already given in code. Then don't ask for path
    if PDF_FILE_PATH == None:
        get_pdf_file_path()
    else:
        if not os.path.isfile(PDF_FILE_PATH):
            print(colored('The file path you given is not valid path', 'red'))
            exit()

    # Path of database file
    DB_FILE_PATH = f'{DB_FOLDER_NAME}/{PDF_FILE_PATH.split("/")[-1]}.db'

    # creating directory if not exisits
    if not os.path.isdir(DB_FOLDER_NAME):
        os.mkdir(DB_FOLDER_NAME)
    
    # If db file already exists then ask to delete old and make new or cancel
    if os.path.isfile(DB_FILE_PATH):
        print('DB File already exists.\n' + 
            colored('Old DB file will be deleted\n\n', 'red') + 
            'Do you still want to continue? (y/N):', end='')
        response = input()
        if not response in ['y', 'Y', "yes", 'Yes']:
            print('Exiting from program...')
            exit()
        try:
            os.remove(DB_FILE_PATH)
        except:
            print(colored("Something went wrong DB file not deleted.", 'red'))
            exit()

    try:
        extract_data_from_pdf()
    except Exception as e:
        print('EXCEPTION: ', e)
        print(f"{colored('[Program Stopped]', 'red')}\n Deleting DB File")
        os.remove(DB_FILE_PATH)