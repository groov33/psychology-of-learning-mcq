import json
import re

qs = json.load(open('data/questions.json', encoding='utf-8'))
print(f"Checking explanation text across all {len(qs)} questions...")
count = 0
for q in qs:
    exp = q.get('explanation', '')
    m = re.findall(r'\b(?:option|opt|choice)\s+([A-Ea-e])\b', exp, re.I)
    if m:
        for let in m:
            let_u = let.upper()
            if let_u not in q['answer']:
                print(f"DISCREPANCY IN EXPLANATION {q['id']}: Exp mentions Option {let_u}, but answer is {q['answer']}")
                print(f"  Exp: {exp}")
                count += 1
if count == 0:
    print("ALL explanations with option mentions 100% MATCH assigned answers!")
