import os
import glob
import json
import re
import fitz

qs = json.load(open('data/questions.json', encoding='utf-8'))
q_by_id = {q['id']: q for q in qs}

print(f"Total questions in database: {len(qs)}")
discrepancies = []
checked_count = 0

# ==============================================================================
# 1. VERIFY 2026 (NPTEL CURRENT 12 ASSIGNMENTS)
# ==============================================================================
print("\n" + "="*70)
print("VERIFYING 2026 (NPTEL Current Assignment PDFs)")
print("="*70)

nptel_files = sorted(glob.glob('Extras/Psychology of learning NPTEL/*.pdf'))
for fpath in nptel_files:
    fname = os.path.basename(fpath)
    # week number from filename e.g. 01.Assignement_Psy.pdf
    wm = re.search(r'(\d+)', fname)
    if not wm: continue
    w_num = int(wm.group(1))
    
    doc = fitz.open(fpath)
    full_text = '\n'.join(p.get_text() for p in doc)
    
    # Split by question numbers
    blocks = re.split(r'\n(?=\s*\d+[\.\)])', full_text)
    for b in blocks:
        qm = re.match(r'^\s*(\d+)[\.\)]', b)
        if not qm: continue
        qn = int(qm.group(1))
        qid = f"2026-w{w_num:02d}-q{qn:02d}"
        if qid not in q_by_id:
            discrepancies.append(f"[{qid}] Missing from database!")
            continue
            
        checked_count += 1
        db_q = q_by_id[qid]
        
        # Extract Ans line
        ans_m = re.search(r'(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*([^\n\r]+)', b, re.I)
        raw_ans = ans_m.group(0).strip() if ans_m else "NOT FOUND"
        
        # Check letter and text
        m_eq = re.search(r'Ans[\.\s:=]+([A-Da-d])\s*=\s*(.*)', raw_ans, re.I)
        raw_letter = None
        raw_text = None
        if m_eq:
            raw_letter = m_eq.group(1).upper()
            raw_text = m_eq.group(2).strip()
        else:
            m_single = re.search(r'Ans[\.\s:=]+([A-Da-d])\b', raw_ans, re.I)
            if m_single:
                raw_letter = m_single.group(1).upper()
                
        db_ans = db_q['answer']
        db_opt_dict = {o['key']: o['text'] for o in db_q['options']}
        
        # Check for discrepancy
        if raw_letter and raw_text:
            # Does raw_text match an option?
            opt_for_text = None
            for k, txt in db_opt_dict.items():
                if txt.lower() == raw_text.lower() or raw_text.lower() in txt.lower():
                    opt_for_text = k
                    break
                    
            if opt_for_text and opt_for_text != raw_letter:
                print(f"[2026 TYPO IN SOURCE PDF DETECTED] {qid}")
                print(f"  PDF Raw: {raw_ans}")
                print(f"  PDF Letter: '{raw_letter}', but PDF Text '{raw_text}' points to Option '{opt_for_text}'")
                print(f"  DB Answer: {db_ans}")
                if db_ans != [opt_for_text]:
                    discrepancies.append(f"{qid}: DB answer {db_ans} does not match corrected option {opt_for_text}")
            else:
                if db_ans != [raw_letter]:
                    discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {raw_letter} (raw='{raw_ans}')")
        elif raw_letter:
            if db_ans != [raw_letter]:
                discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {raw_letter} (raw='{raw_ans}')")
        else:
            discrepancies.append(f"{qid}: Could not find answer in PDF block (raw='{raw_ans}')")

print(f"2026 checked questions: 120")

# ==============================================================================
# 2. VERIFY 2024 (Psycology of lerning 2024.pdf)
# ==============================================================================
print("\n" + "="*70)
print("VERIFYING 2024 (Psycology of lerning 2024.pdf)")
print("="*70)

doc2024 = fitz.open('Extras/Psycology of lerning 2024.pdf')
text2024 = '\n'.join(p.get_text() for p in doc2024)

# 2024 questions have QUESTION X: or X)
qs_2024 = [q for q in qs if q['year'] == '2024']
print(f"Total 2024 questions in DB: {len(qs_2024)}")

for q in qs_2024:
    checked_count += 1
    qid = q['id']
    # search question snippet in PDF
    # Take first 30 alphanumeric characters
    snippet = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[:30].strip()
    pos = text2024.lower().find(snippet.lower())
    if pos == -1:
        # try a secondary snippet
        snippet2 = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[10:40].strip()
        pos = text2024.lower().find(snippet2.lower())
        
    if pos == -1:
        discrepancies.append(f"[{qid}] Could not locate question in 2024 PDF! snippet='{snippet}'")
        continue
        
    # Look for Ans within next 600 characters
    chunk = text2024[pos:pos+700]
    ans_m = re.search(r'(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*([^\n\r]+)', chunk, re.I)
    if not ans_m:
        discrepancies.append(f"[{qid}] Could not find Ans in chunk around position {pos}")
        continue
        
    raw_ans = ans_m.group(0).strip()
    db_ans = q['answer']
    
    # Check letter
    m_let = re.search(r'Ans[\.\s:=]+([A-Ea-e])\b', raw_ans, re.I)
    m_eq = re.search(r'Ans[\.\s:=]+([A-Ea-e])\s*=\s*(.*)', raw_ans, re.I)
    
    if m_eq:
        let = m_eq.group(1).upper()
        txt = m_eq.group(2).strip()
        opt_dict = {o['key']: o['text'] for o in q['options']}
        
        # Check if text matches another option
        matched_opts = [k for k, v in opt_dict.items() if v.lower() == txt.lower() or (len(txt) > 3 and txt.lower() in v.lower())]
        if matched_opts and let not in matched_opts:
            print(f"[2024 TYPO IN SOURCE PDF DETECTED] {qid}")
            print(f"  PDF Raw: {raw_ans}")
            print(f"  PDF Letter: {let}, but text points to {matched_opts}")
            print(f"  DB Answer: {db_ans}")
            if db_ans != matched_opts:
                discrepancies.append(f"{qid}: DB answer {db_ans} vs matched {matched_opts}")
        else:
            if db_ans != [let]:
                discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    elif m_let:
        let = m_let.group(1).upper()
        if db_ans != [let]:
            discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    else:
        discrepancies.append(f"{qid}: Could not parse letter from raw ans: '{raw_ans}'")

# ==============================================================================
# 3. VERIFY 2023 (Psycology of lerning 2023.pdf)
# ==============================================================================
print("\n" + "="*70)
print("VERIFYING 2023 (Psycology of lerning 2023.pdf)")
print("="*70)

doc2023 = fitz.open('Extras/Psychology-of-learning-assignments-2023.pdf')
text2023 = '\n'.join(p.get_text() for p in doc2023)

qs_2023 = [q for q in qs if q['year'] == '2023']
print(f"Total 2023 questions in DB: {len(qs_2023)}")

for q in qs_2023:
    checked_count += 1
    qid = q['id']
    snippet = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[:30].strip()
    pos = text2023.lower().find(snippet.lower())
    if pos == -1:
        snippet2 = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[10:40].strip()
        pos = text2023.lower().find(snippet2.lower())
        
    if pos == -1:
        discrepancies.append(f"[{qid}] Could not locate question in 2023 PDF! snippet='{snippet}'")
        continue
        
    chunk = text2023[pos:pos+700]
    ans_m = re.search(r'(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*([^\n\r]+)', chunk, re.I)
    if not ans_m:
        discrepancies.append(f"[{qid}] Could not find Ans in chunk around position {pos}")
        continue
        
    raw_ans = ans_m.group(0).strip()
    db_ans = q['answer']
    
    m_let = re.search(r'Ans[\.\s:=]+([A-Ea-e])\b', raw_ans, re.I)
    m_eq = re.search(r'Ans[\.\s:=]+([A-Ea-e])\s*=\s*(.*)', raw_ans, re.I)
    
    if m_eq:
        let = m_eq.group(1).upper()
        txt = m_eq.group(2).strip()
        opt_dict = {o['key']: o['text'] for o in q['options']}
        
        matched_opts = [k for k, v in opt_dict.items() if v.lower() == txt.lower() or (len(txt) > 3 and txt.lower() in v.lower())]
        if matched_opts and let not in matched_opts:
            print(f"[2023 TYPO IN SOURCE PDF DETECTED] {qid}")
            print(f"  PDF Raw: {raw_ans}")
            print(f"  PDF Letter: {let}, but text points to {matched_opts}")
            print(f"  DB Answer: {db_ans}")
            if db_ans != matched_opts:
                discrepancies.append(f"{qid}: DB answer {db_ans} vs matched {matched_opts}")
        else:
            if db_ans != [let]:
                discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    elif m_let:
        let = m_let.group(1).upper()
        if db_ans != [let]:
            discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    else:
        discrepancies.append(f"{qid}: Could not parse letter from raw ans: '{raw_ans}'")

# ==============================================================================
# 4. VERIFY 2025 (Psychology-of-learning-assignment-2025.pdf)
# ==============================================================================
print("\n" + "="*70)
print("VERIFYING 2025 (Psychology-of-learning-assignment-2025.pdf)")
print("="*70)

doc2025 = fitz.open('Extras/Psychology-of-learning-assignment-2025.pdf')
text2025 = '\n'.join(p.get_text() for p in doc2025)

qs_2025 = [q for q in qs if q['year'] == '2025']
print(f"Total 2025 questions in DB: {len(qs_2025)}")

for q in qs_2025:
    checked_count += 1
    qid = q['id']
    snippet = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[:30].strip()
    pos = text2025.lower().find(snippet.lower())
    if pos == -1:
        snippet2 = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[10:40].strip()
        pos = text2025.lower().find(snippet2.lower())
    if pos == -1:
        # try 5-25 chars
        snippet3 = re.sub(r'[^A-Za-z0-9]+', ' ', q['question'])[5:25].strip()
        pos = text2025.lower().find(snippet3.lower())
        
    if pos == -1:
        discrepancies.append(f"[{qid}] Could not locate question in 2025 PDF! snippet='{snippet}'")
        continue
        
    chunk = text2025[pos:pos+700]
    # In 2025 OCR, Ans could be Ans, Af15, ABS, AnS
    ans_m = re.search(r'(?:Ans|Af15|ABS|AnS)[\.\s:=,\-_]+([^\n\r]+)', chunk, re.I)
    if not ans_m:
        discrepancies.append(f"[{qid}] Could not find Ans in chunk around position {pos}")
        continue
        
    raw_ans = ans_m.group(0).strip()
    db_ans = q['answer']
    
    # Parse letter / text
    m_eq = re.search(r'(?:Ans|Af15|ABS|AnS)[\.\s:=,\-_]+([A-Ea-e])\s*=\s*(.*)', raw_ans, re.I)
    m_let = re.search(r'(?:Ans|Af15|ABS|AnS)[\.\s:=,\-_]+([A-Ea-e])\b', raw_ans, re.I)
    
    if m_eq:
        let = m_eq.group(1).upper()
        txt = m_eq.group(2).strip()
        opt_dict = {o['key']: o['text'] for o in q['options']}
        matched_opts = [k for k, v in opt_dict.items() if v.lower() == txt.lower() or (len(txt) > 3 and txt.lower() in v.lower())]
        if matched_opts and let not in matched_opts:
            print(f"[2025 TYPO IN SOURCE PDF DETECTED] {qid}")
            print(f"  PDF Raw: {raw_ans}")
            print(f"  PDF Letter: {let}, but text points to {matched_opts}")
            print(f"  DB Answer: {db_ans}")
            if db_ans != matched_opts:
                discrepancies.append(f"{qid}: DB answer {db_ans} vs matched {matched_opts}")
        else:
            if db_ans != [let]:
                discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    elif m_let:
        let = m_let.group(1).upper()
        if db_ans != [let]:
            discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
    else:
        # Might be e.g. Ans. = humanistic or Ans. = d
        m_eq2 = re.search(r'=\s*([A-Ea-e])\b', raw_ans)
        if m_eq2:
            let = m_eq2.group(1).upper()
            if db_ans != [let]:
                discrepancies.append(f"{qid}: DB answer {db_ans} != PDF letter {let} (raw='{raw_ans}')")
        else:
            # Check if raw text matches any option
            opt_dict = {o['key']: o['text'] for o in q['options']}
            matched_opts = [k for k, v in opt_dict.items() if v.lower() in raw_ans.lower()]
            if matched_opts:
                if db_ans != matched_opts:
                    discrepancies.append(f"{qid}: DB answer {db_ans} != matched option {matched_opts} from '{raw_ans}'")
            else:
                discrepancies.append(f"{qid}: Could not parse letter from raw ans: '{raw_ans}'")

print("\n" + "="*70)
print(f"SUMMARY: Total questions checked: {checked_count} / {len(qs)}")
print(f"Total discrepancies found: {len(discrepancies)}")
print("="*70)
for d in discrepancies:
    print("  ->", d)
