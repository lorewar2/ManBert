# from model import BertAIRegressor, ChunkedDataset, score_long_document, train
# from torch.utils.data import DataLoader
# from transformers import BertTokenizer
import os
from bs4 import BeautifulSoup
import pymupdf
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from pathlib import Path
from manual_detector import manual_ai_feature_detector
import pandas as pd
import torch.nn as nn
import torch.optim as optim
import os

BATCH_SIZE = 16
MAX_LEN = 512
STRIDE = 512
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
AI_INFO_SAVE_PATH = "./data/ai_info_list.txt"

class DNN_model(nn.Module):
    def __init__(self):
        super(DNN_model, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)
    
def run_bert_and_manual_save():
    tokenizer = AutoTokenizer.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    model = AutoModelForSequenceClassification.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    path = './train_set/'
    files = sorted(os.listdir(path))
    for file in files:
        #print(file.name) # Just the name
        #print(file.absolute()) # The full path
        extracted_text = extract_text_from_pdf_xml(path + file)
        scores = manual_ai_feature_detector(extracted_text)
        score = score_long_document(extracted_text, model, tokenizer)
        scores = scores + [score]
        print(file, scores)
        with open("train_scores.txt", "a", encoding="utf-8") as f:
            f.write(file + "," + str(scores).replace("[", "").replace("]", "").replace(" ", "") + "\n")
    return

def load_data(csv_path):
    df = pd.read_csv(csv_path)

    file_paths = df.iloc[:, 0].values
    X = df.iloc[:, 1:9].values.astype("float32")

    y = []
    for path in file_paths:
        num = int(path.split(".")[0])
        if 256 <= num < 768:
            y.append(0.0)
        else:
            y.append(1.0)

    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    return X, y


def machine_learning_model_train(
    train_csv="train.csv",
    val_csv="val.csv",
    test_csv="test.csv",
    epochs=20,
    lr=0.001,
    save_path="model.pth"
):
    # ---- Load datasets ----
    X_train, y_train = load_data(train_csv)
    X_val, y_val = load_data(val_csv)
    X_test, y_test = load_data(test_csv)

    # ---- Model ----
    model = DNN_model()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # ---- Training loop ----
    for epoch in range(epochs):
        # Train
        model.train()
        outputs = model(X_train)
        train_loss = criterion(outputs, y_train)

        optimizer.zero_grad()
        train_loss.backward()
        optimizer.step()

        # ---- Validation & Test ----
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val)

            test_outputs = model(X_test)
            test_loss = criterion(test_outputs, y_test)
            test_acc = compute_accuracy(test_outputs, y_test)
        print(
            f"Epoch {epoch+1}/{epochs} | "
            f"Train: {train_loss.item():.4f} | "
            f"Val: {val_loss.item():.4f} | "
            f"Test: {test_loss.item():.4f} {test_acc:.4f}"
        )
    
    # ---- Save weights ----
    torch.save(model.state_dict(), save_path)
    print(f"Model weights saved to {save_path}")

    return model


def compute_accuracy(outputs, targets):
    # Convert probabilities → 0 or 1
    preds = (outputs >= 0.5).float()
    
    # Compare with ground truth
    correct = (preds == targets).float().sum()
    acc = correct / targets.shape[0]

    return acc.item()

def main():
    tokenizer = AutoTokenizer.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    model = AutoModelForSequenceClassification.from_pretrained("AICodexLab/answerdotai-ModernBERT-base-ai-detector")
    # read the file, save lines  requried dir
    download_info = get_dir_info("./data/paper_download_list.txt")
    ai_info = get_dir_info(AI_INFO_SAVE_PATH)
    to_be_skipped = len(ai_info)
    count = 0
    for line in download_info:
        current_file = line.split("\t")[6]
        print(current_file)
        if current_file == "fail":
            continue
        if count < to_be_skipped:
            count += 1
            continue
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
    elif file_ext == "txt":
        with open(file_name, 'r') as file:
            text_string = file.read()
    #print(text_string)
    return text_string

def score_test_set(
    test_csv="test.csv",
    model_path="model.pth",
    output_csv="predictions.csv"
):
    # ---- Load data ----
    df = pd.read_csv(test_csv)
    file_paths = df.iloc[:, 0].values
    X = df.iloc[:, 1:9].values.astype("float32")

    X = torch.tensor(X, dtype=torch.float32)

    # ---- Load model ----
    model = DNN_model()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # ---- Inference ----
    with torch.no_grad():
        outputs = model(X)
        probs = outputs.squeeze().numpy()   # probabilities
        preds = (outputs >= 0.5).float().squeeze().numpy()  # 0/1 labels

    # ---- Save results ----
    results = pd.DataFrame({
        "file": file_paths,
        "probability": probs,
        "prediction": preds
    })

    results.to_csv(output_csv, index=False)
    print(f"Predictions saved to {output_csv}")

    return results

if __name__ == "__main__":
    #run_bert_and_manual_save()
    machine_learning_model_train(train_csv = "train_scores.txt", test_csv="test_scores.txt", val_csv="val_scores.txt", epochs = 50_000, lr = 0.000005, save_path="model.pth")
    #score_test_set(test_csv="test_scores.txt",model_path="model.pth",output_csv="result.csv")
    #main()
    
