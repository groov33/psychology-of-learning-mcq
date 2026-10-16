import os
import json
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
import test_nptel_parser
import test_2024_parser
import test_2023_parser
import test_2025_parser

def clean_ocr_artifacts(text):
    if not text:
        return ""
    replacements = [
        ('“', '"'),
        ('”', '"'),
        ('’', "'"),
        ('‘', "'"),
        ('–', '-'),
        ('—', '-'),
        (' ,', ','),
        (' .', '.'),
        (' ?', '?'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def apply_curated_fixes(all_qs):
    for q in all_qs:
        qid = q['id']
        
        # 1. 2026-w09-q07
        if qid == '2026-w09-q07':
            q['question'] = 'Learners may multitask when engaging in an online course, which could be resulting in ____.'
            q['options'] = [
                {'key': 'A', 'text': 'hyperfocus'},
                {'key': 'B', 'text': 'better retrieval'},
                {'key': 'C', 'text': 'shorter attention spans'},
                {'key': 'D', 'text': 'None of the given'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-9 (slide no.19) for better understanding.'
            
        # 1b. 2026-w06-q07
        elif qid == '2026-w06-q07':
            q['question'] = 'Which of the following is a facilitator of EQ?'
            q['options'] = [
                {'key': 'A', 'text': 'optimism'},
                {'key': 'B', 'text': 'happiness'},
                {'key': 'C', 'text': 'independence'},
                {'key': 'D', 'text': 'all of the given'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-6 (slide no.18) for better understanding. (Note: NPTEL assignment PDF had a typographical error stating "Ans. a=" instead of "Ans. d= all of the given").'
            
        # 2. 2025-w03-q02
        elif qid == '2025-w03-q02':
            q['question'] = '____ refers to connections between the nerve cells.'
            q['options'] = [
                {'key': 'A', 'text': 'Storage'},
                {'key': 'B', 'text': 'Synapses'},
                {'key': 'C', 'text': 'Neuron'},
                {'key': 'D', 'text': 'Blood'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-3 (slide no.02) for better understanding.'
            
        # 3. 2025-w03-q06
        elif qid == '2025-w03-q06':
            q['question'] = 'Which of the following is not an assumption of the information processing view?'
            q['options'] = [
                {'key': 'A', 'text': 'Information is processed in steps or stages'},
                {'key': 'B', 'text': 'There are limits on how much information can be processed'},
                {'key': 'C', 'text': 'The human information processing system is interactive'},
                {'key': 'D', 'text': 'Information processing is analogous to computer processing'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-3 (slide no.9) for better understanding.'
            
        # 4. 2025-w06-q02
        elif qid == '2025-w06-q02':
            q['question'] = 'EQ is used to measure ____.'
            q['options'] = [
                {'key': 'A', 'text': 'cognitive intelligence'},
                {'key': 'B', 'text': 'social intelligence'},
                {'key': 'C', 'text': 'emotional intelligence'},
                {'key': 'D', 'text': 'attention'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-6 (slide no.03) for better understanding.'
            
        # 5. 2025-w07-q02
        elif qid == '2025-w07-q02':
            q['question'] = "Manual or physical skills come under ____ component of Bloom's taxonomy."
            q['options'] = [
                {'key': 'A', 'text': 'Cognitive'},
                {'key': 'B', 'text': 'Affective'},
                {'key': 'C', 'text': 'Psychomotor'},
                {'key': 'D', 'text': 'Physical'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-7 (slide no.04) for better understanding.'
            
        # 6. 2024-w02-q01
        elif qid == '2024-w02-q01':
            q['question'] = '____ is known as the father of modern psychology.'
            q['options'] = [
                {'key': 'A', 'text': 'Sigmund Freud'},
                {'key': 'B', 'text': 'Wilhelm Wundt'},
                {'key': 'C', 'text': 'John Watson'},
                {'key': 'D', 'text': 'Lev Vygotsky'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-2 (slide no.33) for better understanding.'

def build_all():
    os.makedirs('data', exist_ok=True)
    
    print("Parsing NPTEL (2026 / Current)...")
    nptel_qs = test_nptel_parser.parse_nptel_folder()
    
    print("Parsing 2024 PYQ...")
    pyq2024 = test_2024_parser.parse_2024()
    
    print("Parsing 2023 PYQ...")
    pyq2023 = test_2023_parser.parse_2023()
    
    print("Parsing 2025 PYQ...")
    pyq2025 = test_2025_parser.parse_2025()
    
    all_qs = []
    
    for q_list in [nptel_qs, pyq2025, pyq2024, pyq2023]:
        for q in q_list:
            q['question'] = clean_ocr_artifacts(q['question'])
            for opt in q['options']:
                opt['text'] = clean_ocr_artifacts(opt['text'])
            if 'explanation' in q:
                q['explanation'] = clean_ocr_artifacts(q['explanation'])
            q.pop('raw_ans', None)
            all_qs.append(q)
            
    # Apply precise curated fixes
    apply_curated_fixes(all_qs)
            
    print(f"\n================ TOTAL QUESTIONS: {len(all_qs)} ================")
    
    by_year = {}
    by_week = {}
    missing_ans = 0
    missing_opts = 0
    
    for q in all_qs:
        y = q['year']
        w = q['week']
        by_year[y] = by_year.get(y, 0) + 1
        by_week[w] = by_week.get(w, 0) + 1
        
        if not q['answer']:
            missing_ans += 1
        if len(q['options']) < 2:
            missing_opts += 1
            
    print(f"By Year: {by_year}")
    print(f"By Week: {sorted(by_week.items())}")
    print(f"Missing answers: {missing_ans}")
    print(f"Missing options: {missing_opts}")
    
    # Save to data/questions.json
    output_path = os.path.join('data', 'questions.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_qs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_qs)} questions to {output_path}")
    
    # Also save to data/questions-data.js for standalone browser support
    js_path = os.path.join('data', 'questions-data.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.NPTEL_QUESTIONS = ' + json.dumps(all_qs, ensure_ascii=False) + ';\n')
    print(f"Saved {len(all_qs)} questions to {js_path}")
    
    summary = {
        'totalQuestions': len(all_qs),
        'byYear': by_year,
        'byWeek': {f'Week {k}': v for k, v in sorted(by_week.items())},
        'years': [
            {'id': '2026', 'label': '2026 (Current Course Assignment)', 'count': by_year.get('2026', 0)},
            {'id': '2025', 'label': '2025 Assignment PYQs', 'count': by_year.get('2025', 0)},
            {'id': '2024', 'label': '2024 Assignment PYQs', 'count': by_year.get('2024', 0)},
            {'id': '2023', 'label': '2023 Assignment PYQs', 'count': by_year.get('2023', 0)},
        ],
        'weeks': sorted(list(by_week.keys()))
    }
    with open(os.path.join('data', 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    return all_qs

if __name__ == '__main__':
    build_all()
