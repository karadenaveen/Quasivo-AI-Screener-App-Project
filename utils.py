import os
import json
import datetime
from PyPDF2 import PdfReader

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages])

def save_to_json(data, folder="data"):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(folder, f"session_{timestamp}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
