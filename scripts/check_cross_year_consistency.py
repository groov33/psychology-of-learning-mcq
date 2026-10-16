import json
import re

qs = json.load(open('data/questions.json', encoding='utf-8'))

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return text.strip()

questions_by_norm = {}
for q in qs:
    norm = normalize_text(q['question'])
    if len(norm) < 15:
        continue
    if norm not in questions_by_norm:
        questions_by_norm[norm] = []
    questions_by_norm[norm].append(q)

duplicates = {k: v for k, v in questions_by_norm.items() if len(v) > 1}
print(f"Total repeated questions across years: {len(duplicates)}")

conflict_count = 0
for norm, group in duplicates.items():
    # Compare the actual answer option texts across the repetitions
    answers_texts = []
    for q in group:
        opt_dict = {o['key']: o['text'].strip().lower() for o in q['options']}
        ans_text = tuple(sorted([opt_dict.get(a, '') for a in q['answer']]))
        answers_texts.append((q['id'], q['year'], q['answer'], ans_text))
        
    first_ans_text = answers_texts[0][3]
    for item in answers_texts[1:]:
        if item[3] != first_ans_text:
            print(f"\n[CONFLICT DETECTED ACROSS REPEATED QUESTIONS]")
            print(f"  Q: {group[0]['question']}")
            for q_id, y, ans_key, a_txt in answers_texts:
                print(f"    - {q_id} ({y}): Key={ans_key} -> Text={a_txt}")
            conflict_count += 1
            break

if conflict_count == 0:
    print("ALL repeated questions across 2023, 2024, 2025, and 2026 have 100% IDENTICAL and CONSISTENT correct answer texts!")
