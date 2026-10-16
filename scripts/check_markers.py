import json
import re

qs = json.load(open('data/questions.json', encoding='utf-8'))
for q in qs:
    for o in q['options']:
        if re.search(r'\b[b-e][,\.]\s*', o['text'], re.I):
            print(f"{q['id']} {o['key']}: {o['text']}")
