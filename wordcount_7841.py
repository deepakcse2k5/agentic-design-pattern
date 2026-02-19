# This Python program implements the following use case:
#Write code which takes a command line input of a word doc or docx file and opens it and counts the number of words , and characters in it and prints all

```python
import sys
from docx import Document
import os
from docx.opc.exceptions import PackageNotFoundError

def validate_file(file_path):
    if not file_path.endswith('.docx'):
        raise ValueError(f"Invalid file type: {file_path}. The file must be a .docx file.")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}.")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"File cannot be read: {file_path}.")

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
    except PackageNotFoundError:
        raise ValueError("The file is not a valid .docx document.")
    except IOError as e:
        raise ValueError(f"Error opening file: {e}")
    return ' '.join(paragraph.text for paragraph in doc.paragraphs)

def count_words_and_characters(text):
    words = text.split()
    return len(words), len(text)

def main(file_path):
    try:
        validate_file(file_path)
        full_text = extract_text_from_docx(file_path)
        if not full_text.strip():
            print("The document is empty.")
            return
        num_words, num_characters = count_words_and_characters(full_text)
        print(f"Number of words: {num_words}")
        print(f"Number of characters: {num_characters}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file.docx>")
    else:
        main(sys.argv[1])