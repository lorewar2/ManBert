# from model import BertAIRegressor, ChunkedDataset, score_long_document, train
# from torch.utils.data import DataLoader
# from transformers import BertTokenizer
import os
from bs4 import BeautifulSoup
import pymupdf
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

BATCH_SIZE = 16
MAX_LEN = 512
STRIDE = 512
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
AI_INFO_SAVE_PATH = "./data/ai_info_list.txt"

def main():
    tokenizer = AutoTokenizer.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    model = AutoModelForSequenceClassification.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    # read the file, save lines  requried dir
    download_info = get_dir_info("./data/paper_download_list.txt")
    ai_info = get_dir_info(AI_INFO_SAVE_PATH)[-1]
    count = 0
    start = False
    for line in download_info:
        if line.split("\t")[0] == ai_info.split("\t")[0]:
            print("SAME!!")
            start = True
        current_file = line.split("\t")[6]
        print(current_file)
        extracted_text = extract_text_from_pdf_xml(current_file)
        score = score_long_document(extracted_text, model, tokenizer)
        print(count, score)
        count += 1
        with open(AI_INFO_SAVE_PATH, "a", encoding="utf-8") as f:
            f.write(line + " " + str(score) + "\n")
    return

def chunk_text(text, tokenizer, max_len=MAX_LEN, stride=STRIDE):
    tokens = tokenizer(
        text,
        add_special_tokens=False,
        return_attention_mask=False
    )["input_ids"]
    chunks = []
    for i in range(0, len(tokens), stride):
        chunk_tokens = tokens[i:i + max_len]
        encoded = tokenizer.prepare_for_model(
            chunk_tokens,
            max_length=max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        chunks.append({
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0)
        })
    return chunks

def score_long_document(text, model, tokenizer):
    model.eval()
    chunks = chunk_text(text, tokenizer)
    sum = 0.0
    count = 0
    with torch.no_grad():
        for chunk in chunks:
            input_ids = chunk["input_ids"].unsqueeze(0).to(DEVICE)
            attention_mask = chunk["attention_mask"].unsqueeze(0).to(DEVICE)
            score = model(input_ids, attention_mask)
            prediction = score.logits.argmax(dim=1).item()
            count += 1
            sum += float(prediction)
    return (sum / (count + 1))

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
    