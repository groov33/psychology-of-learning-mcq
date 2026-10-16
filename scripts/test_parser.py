import os
import re
import glob
import fitz
import json

def clean_text(text):
    if not text:
        return ""
    # Remove OCR junk from headers
    text = re.sub(r'NI[\s]*I\s*ML\s*Online\s*Certification\s*Courses', '', text, flags=re.I)
    text = re.sub(r'NPTEL\s*Online\s*Certification\s*Courses', '', text, flags=re.I)
    text = re.sub(r'Indian\s*Institute\s*of[\s]*[TJ]echnology\s*Kharagpur', '', text, flags=re.I)
    text = re.sub(r'[\s]*Scanned\s*with\s*OKEN\s*Scanner[i]?', '', text, flags=re.I)
    text = re.sub(r'Psychology\s*of\s*L[ec]a[mr]ing', '', text, flags=re.I)
    text = re.sub(r'TYPE\s*OF\s*QUESTION:\s*(?:MCQ|MSQ)[\s/]*(?:MCQ|MSQ)?', '', text, flags=re.I)
    text = re.sub(r'Number\s*of\s*questions[\.:\s]*\d+', '', text, flags=re.I)
    text = re.sub(r'[-_]{10,}', '', text)
    # Replace non-breaking spaces or replacement chars
    text = text.replace('\xa0', ' ').replace('', "'")
    return text.strip()

print("Ready to test parsers.")
