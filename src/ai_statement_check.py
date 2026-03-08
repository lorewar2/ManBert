import os
from bs4 import BeautifulSoup
import pymupdf
import re

def main():
    # read the file, save lines  requried dir
    download_info = get_dir_info("./data/paper_download_list.txt")
    count = 0
    for line in download_info:
        current_file = line.split("\t")[6]
        print(current_file)
        if current_file == "fail":
            continue
        extracted_text = extract_text_from_pdf_xml(current_file)
        ai_statement_positive = is_ai_statement_included(extracted_text)
        if ai_statement_positive:
            count += 1
            with open("./data/with_ai_statement.txt", "a", encoding="utf-8") as f:
                f.write(line + "\n")
            print(count)
    return

def is_ai_statement_included(extracted_text):
    if not extracted_text:
        return False

    text = extracted_text.lower()

    # Negative AI declarations
    negative_patterns = [
        r"\bno\s+(gen|generative)?\s*ai\s+(was|were)\s+used\b",
        r"\bno\s+(gen|generative)?\s*ai\s+tools?\s+(were|was)\s+used\b",
        r"\bno\s+artificial\s+intelligence\s+(was|were)\s+used\b",
        r"\bdid\s+not\s+use\s+(gen|generative)?\s*ai\b",
        r"\bwithout\s+using\s+(gen|generative)?\s*ai\b",
        r"\bdeclare\s+that\s+no\s+(gen|generative)?\s*ai\s+was\s+used\b"
    ]

    for pattern in negative_patterns:
        if re.search(pattern, text):
            return False

    # Positive AI usage statements
    positive_patterns = [
        r"\bai[- ]assisted\b",
        r"\bai[- ]generated\b",
        r"\busing\s+(gen|generative)?\s*ai\b",
        r"\bused\s+(gen|generative)?\s*ai\b",
        r"\bai\s+(was|were)\s+used\b",
        r"\bchatgpt\s+was\s+used\b",
        r"\busing\s+chatgpt\b",
        r"\bgenerated\s+with\s+chatgpt\b",
        r"\busing\s+gpt[- ]?\d\b",
        r"\bassisted\s+by\s+(an\s+)?ai\b",
        r"\bcontent\s+generated\s+by\s+ai\b"
    ]

    for pattern in positive_patterns:
        if re.search(pattern, text):
            return True

    return False

def get_dir_info(file_path):
    line_array = []
    if os.path.isfile(file_path):
        # open the file and load up the dict
        with open(file_path, 'r', encoding="utf-8") as file:
            for line in file:
                line_array.append(line.strip())
    return line_array

def extract_text_from_pdf_xml(file_name):
    text_string = ""
    file_ext = file_name[-3:]
    if file_ext == "xml":
        filehandle = open(file_name)
        soup = BeautifulSoup(filehandle)
        pageText = soup.findAll(text=True)
        big_text_chunks = []
        for text in pageText:
            if len(text) > 200:
                text_string = "\n".join([text_string, text])
        if len(text_string) <= 200:
            text_string = ""
            for text in pageText:
                if len(text) > 100:
                    text_string = "\n".join([text_string, text])

    elif file_ext == "pdf":
        doc = pymupdf.open(file_name) # open a document
        for page in doc: # iterate the document pages
            text = page.get_text() # get plain text encoded as UTF-8
            #print(text)
            text_string = "\n".join([text_string, text])
    #print(text_string)
    return text_string

if __name__ == "__main__":
    main()