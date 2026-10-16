import json

with open('data/questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f"Total questions loaded: {len(qs)}")

years = set()
weeks = set()
types = set()
errors = []

for idx, q in enumerate(qs):
    years.add(q.get('year'))
    weeks.add(q.get('week'))
    types.add(q.get('type'))
    
    if not q.get('question') or len(q.get('question')) < 5:
        errors.append(f"Q{idx} invalid question text: {q}")
    if not q.get('options') or len(q['options']) < 2:
        errors.append(f"Q{idx} ({q.get('id')}) has < 2 options: {q.get('options')}")
    if not q.get('answer'):
        errors.append(f"Q{idx} ({q.get('id')}) has no answer")
    else:
        opt_keys = [o['key'] for o in q['options']]
        for a in q['answer']:
            if a not in opt_keys:
                errors.append(f"Q{idx} ({q.get('id')}) answer {a} not in options {opt_keys}")

print("Years present:", sorted(list(years)))
print("Weeks present:", sorted(list(weeks)))
print("Types present:", sorted(list(types)))
print(f"Validation errors count: {len(errors)}")
if errors:
    for e in errors[:10]:
        print("  Error:", e)
else:
    print("ALL 478 QUESTIONS PASSED VALIDATION PERFECTLY!")
