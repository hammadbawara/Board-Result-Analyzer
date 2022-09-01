# importing required modules
import os
import re
import json
import PyPDF2
from termcolor import colored
from tqdm import tqdm

PDF_FILE_NAME = "MA2022 GAZETTE.pdf"
TEXT_FILE_NAME = f'{PDF_FILE_NAME}.txt'


def create_text_file():
    # creating a pdf file object
    pdfFileObj = open('MA2022 GAZETTE.pdf', 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    number_of_pages = pdfReader.numPages

    student_result_pattern = "[0-9]{6} +[A-Z ]+[-]* [A-Z0-9,]*"
    institute_name_pattern = "[0-9]{6}-[A-Z., ()-]*"

    with open(TEXT_FILE_NAME, "w") as f:
        f.write("")

    text_file = open(TEXT_FILE_NAME, "a")

    print(colored("EXTRACTING TEXT FROM PDF ..........", "green"))

    for i in tqdm(range(number_of_pages)):
        pageObj = pdfReader.getPage(i)
        page_text = pageObj.extractText()

        page_text_lines = page_text.split("\n")

        for i, line in enumerate(page_text_lines):
            line = line.strip()
            if re.match(student_result_pattern, line):
                if i == 41:
                    two_students = re.findall(student_result_pattern, line)
                    for student in two_students:
                        text_file.write(f'{student}\n')
                else:
                    text_file.write(f'{i} - {line}\n')
            elif re.match(institute_name_pattern, line):
                text_file.write(f'\n\n{line}\n')

    # closing the pdf file object
    pdfFileObj.close()


if __name__ == '__main__':
    if not os.path.isfile(TEXT_FILE_NAME):
        create_text_file()
