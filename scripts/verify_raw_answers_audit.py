import os
import sys
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import test_nptel_parser
import test_2024_parser
import test_2023_parser
import test_2025_parser

db_qs = json.load(open('data/questions.json', encoding='utf-8'))
db_by_id = {q['id']: q for q in db_qs}

print("Running raw PDF parsers...")
nptel_qs = test_nptel_parser.parse_nptel_folder()
pyq2025 = test_2025_parser.parse_2025()
pyq2024 = test_2024_parser.parse_2024()
pyq2023 = test_2023_parser.parse_2023()

all_raw = nptel_qs + pyq2025 + pyq2024 + pyq2023
print(f"\nTotal raw parsed questions from all source PDFs: {len(all_raw)}")
print(f"Total questions in database: {len(db_qs)}")

discrepancies = []
text_letter_mismatches = []
special_notes = []

for raw in all_raw:
    qid = raw['id']
    if qid not in db_by_id:
        discrepancies.append(f"[{qid}] Missing from database!")
        continue
        
    db_q = db_by_id[qid]
    raw_ans = raw.get('raw_ans', '').strip()
    db_ans = db_q['answer']
    db_opts = {o['key']: o['text'] for o in db_q['options']}
    
    # 1. Check if raw_ans has an '=' with text
    # e.g., "a= all of the given" or "B= simulation" or "= c"
    eq_match = re.search(r'([A-Ea-e])\s*=\s*(.*)', raw_ans)
    single_let_match = re.search(r'^([A-Ea-e])\b', raw_ans)
    
    if eq_match:
        let = eq_match.group(1).upper()
        txt = eq_match.group(2).strip()
        
        # Check which DB option has txt
        txt_clean = txt.lower().strip()
        opt_matches = []
        for k, opt_txt in db_opts.items():
            ot_clean = opt_txt.lower().strip()
            if ot_clean == txt_clean:
                opt_matches.append(k)
            elif len(txt_clean) > 4 and (txt_clean in ot_clean or ot_clean in txt_clean):
                opt_matches.append(k)
                
        if opt_matches:
            if let not in opt_matches:
                text_letter_mismatches.append({
                    'id': qid,
                    'raw_ans': raw_ans,
                    'pdf_letter': let,
                    'pdf_text': txt,
                    'text_points_to': opt_matches,
                    'db_answer': db_ans,
                    'question': db_q['question'],
                    'options': db_opts
                })
            else:
                # Letter and text agree
                if db_ans != [let]:
                    discrepancies.append(f"[{qid}] DB answer {db_ans} != PDF answer {[let]} (raw='{raw_ans}')")
        else:
            # Text didn't fuzzy match directly (maybe OCR typos or short), check letter
            if db_ans != [let]:
                discrepancies.append(f"[{qid}] DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}', txt='{txt}')")
    elif single_let_match:
        let = single_let_match.group(1).upper()
        if db_ans != [let]:
            discrepancies.append(f"[{qid}] DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    else:
        # Check other formats e.g. "= humanistic" or "= c" or pure text
        m_eq_letter = re.search(r'=\s*([A-Ea-e])\b', raw_ans)
        if m_eq_letter:
            let = m_eq_letter.group(1).upper()
            if db_ans != [let]:
                discrepancies.append(f"[{qid}] DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
        else:
            special_notes.append({
                'id': qid,
                'raw_ans': raw_ans,
                'db_answer': db_ans,
                'db_opts': db_opts
            })

print("\n" + "="*80)
print(f"1. TYPOS IN SOURCE PDFS WHERE PDF LETTER != PDF TEXT: {len(text_letter_mismatches)}")
print("="*80)
for m in text_letter_mismatches:
    print(f"[{m['id']}]")
    print(f"  PDF Raw Ans: '{m['raw_ans']}'")
    print(f"  PDF Letter: '{m['pdf_letter']}' vs PDF Text points to: {m['text_points_to']}")
    print(f"  DB Answer: {m['db_answer']}")
    print(f"  Question: {m['question'][:70]}...")
    print(f"  Options: {m['options']}")
    print()

print("\n" + "="*80)
print(f"2. DIRECT DISCREPANCIES BETWEEN DB ANSWER AND PDF RAW ANSWER: {len(discrepancies)}")
print("="*80)
for d in discrepancies:
    print("  ->", d)

print("\n" + "="*80)
print(f"3. NON-STANDARD RAW ANS FORMATS: {len(special_notes)}")
print("="*80)
for s in special_notes:
    print(f"[{s['id']}] raw_ans='{s['raw_ans']}' db_ans={s['db_answer']} opts={s['db_opts']}")
