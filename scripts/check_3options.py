import json

qs = json.load(open('data/questions.json', encoding='utf-8'))
print('--- 3-OPTION QUESTIONS ---')
for q in qs:
    if len(q['options']) == 3:
        keys = [o['key'] for o in q['options']]
        print(f"{q['id']}: keys={keys} ans={q['answer']}")
        print(f"  Q: {q['question']}")
        for o in q['options']:
            print(f"    {o['key']}: {o['text']}")
        print(f"  Exp: {q.get('explanation')}")
        print()
