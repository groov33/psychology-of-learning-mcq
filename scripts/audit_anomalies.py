import json
import re

qs = json.load(open('data/questions.json', encoding='utf-8'))
print(f"Total questions: {len(qs)}")

print("\n--- 1. MERGED OPTIONS (b, c, d inside option text) ---")
for q in qs:
    for o in q['options']:
        if re.search(r'\b[b-d][\.,\)]\s+', o['text'], re.I):
            print(f"[{q['id']}] Option {o['key']}: {o['text']}")

print("\n--- 2. OPTION A SWALLOWED IN QUESTION TEXT ---")
for q in qs:
    # Look for a. or a, near the end or middle of question text
    m = re.search(r'\s+([aA][\.,\)]\s+[A-Za-z0-9].*)$', q['question'])
    if m:
        print(f"[{q['id']}] Q: {q['question']}")
        print(f"      Matched: {m.group(1)}")

print("\n--- 3. NON-4-OPTION QUESTIONS (excluding 2-option True/False) ---")
for q in qs:
    n = len(q['options'])
    keys = [o['key'] for o in q['options']]
    if n not in (2, 4):
        print(f"[{q['id']}] {n} options (keys={keys}):")
        print(f"   Q: {q['question']}")
        for o in q['options']:
            print(f"   {o['key']}: {o['text']}")

print("\n--- 4. TRUE/FALSE QUESTIONS WITH WEIRD KEYS ---")
for q in qs:
    n = len(q['options'])
    keys = [o['key'] for o in q['options']]
    if n == 2 and keys != ['A', 'B']:
        print(f"[{q['id']}] 2 options but keys={keys}")

print("\n--- 5. CHECK 5-OPTION QUESTIONS (A, B, C, D, E) ---")
e_count = 0
for q in qs:
    keys = [o['key'] for o in q['options']]
    if 'E' in keys:
        e_count += 1
print(f"Total questions with option E: {e_count}")
# Let's inspect a few to see if E is genuine or an artifact
sample_e = [q for q in qs if 'E' in [o['key'] for o in q['options']]][:3]
for q in sample_e:
    print(f"[{q['id']}] Ans: {q['answer']} Options:")
    for o in q['options']:
        print(f"   {o['key']}: {o['text']}")

print("\n--- 6. EMPTY OR VERY SHORT OPTION TEXTS ---")
for q in qs:
    for o in q['options']:
        if len(o['text'].strip()) <= 1:
            print(f"[{q['id']}] Option {o['key']} has short/empty text: '{o['text']}'")

