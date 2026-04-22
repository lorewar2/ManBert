from bs4 import BeautifulSoup
import pymupdf
import sys

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
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    file_name = sys.argv[1]
    result = extract_text_from_pdf_xml(file_name)
    print(result)