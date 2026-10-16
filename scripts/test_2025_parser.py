import fitz
import re

def parse_2025():
    doc = fitz.open('Extras/Psychology-of-learning-assignment-2025.pdf')
    
    week_ranges = [
        (1, 1, 4),
        (2, 5, 8),
        (3, 9, 12),
        (4, 13, 16),
        (5, 17, 21),
        (6, 22, 26),
        (7, 27, 30),
        (8, 31, 34),
        (9, 35, 39),
        (10, 40, 43),
        (11, 44, 48)
    ]
    
    results = []
    
    for w_num, start_p, end_p in week_ranges:
        text_parts = []
        for p in range(start_p - 1, end_p):
            t = doc[p].get_text()
            lines = t.splitlines()
            cleaned_lines = []
            for l in lines:
                ls = l.strip()
                if any(h in ls.lower() for h in [
                    'online certification courses',
                    'institute of',
                    'oken scanner',
                    'psychology of',
                    'th pe',
                    'number of questions',
                    'type of question'
                ]):
                    continue
                if re.search(r'July\s+202[0-9a-z].*?Assignment', ls, re.I):
                    continue
                cleaned_lines.append(l)
            text_parts.append('\n'.join(cleaned_lines))
            
        full_text = '\n'.join(text_parts)
        
        # Specific OCR text repairs before question splitting
        if w_num == 2:
            full_text = re.sub(r'(\n\s*)In\s*conoltioning,\s*presentation', r'\1 6) In conditioning, presentation', full_text)
            full_text = re.sub(r'/1!E\s*TIU\s*\n\s*8:', r'\n 8)', full_text)
        elif w_num == 4:
            full_text = re.sub(r'(\n\s*)Bloom\'s\s*Taxonomy\s*is\s*a\s*system', r'\1 6) Bloom\'s Taxonomy is a system', full_text)
        elif w_num == 5:
            full_text = re.sub(r'(\n\s*)s\)\s*thBofy\s*suggests', r'\1 6) Theory suggests', full_text)
            full_text = re.sub(r'(\n\s*)s\)\s*theory\s*is\s*based', r'\1 8) Theory is based', full_text)
        elif w_num == 6:
            full_text = re.sub(r'\}1\s*STIOK\s*10:?', r'\n10)', full_text)
            full_text = re.sub(r'(\n\s*)Review\s*of\s*literature\s*shows\s*that', r'\1 10) Review of literature shows that', full_text)
        elif w_num == 7:
            full_text = re.sub(r'human!stic', 'humanistic', full_text)
            full_text = re.sub(r'Ans\.\s*=\s*humanistic', 'Ans. = c', full_text)
        elif w_num == 8:
            full_text = re.sub(r'(d\.\s*seven[\s\n]+)(Solution:)', r'\1Ans. = c\n\2', full_text)
        elif w_num == 9:
            full_text = re.sub(r'101\s*\n', r'10) ', full_text)
        elif w_num == 11:
            full_text = re.sub(r'(\n\s*)The\s*theory\s*details\s*the\s*processes\s*of\s*observational', r'\1 6) The theory details the processes of observational', full_text)
            full_text = re.sub(r'ot!vsi\s*io\.s\s*8\.[\s\n]*\)\s*Children', r'8) Children', full_text)
            full_text = re.sub(r'(\n\s*)refers\s*to\s*the\s*anticipated\s*consequences', r'\1 10) What refers to the anticipated consequences', full_text)
            
        # Clean noisy OCR for QUESTION lines completely
        full_text = re.sub(r'(?m)^.*(?:fiS[\'’]FIOfi|ESTI|STIO|nvxs|tJvT|9uxs|9l!rs|ntirs|yvt|th\s*ES|Ot1LS|Ot1S).*$\n?', '', full_text)
        
        # Standardize OCR answer tokens: ABS., Af15., Ans,, Ans -, AnS,
        full_text = re.sub(r'\b(?:ABS|Af15|AnS|Ans)[\.,\s\-_=]+', 'Ans. = ', full_text, flags=re.I)
        
        # Questions start with 1) to 10)
        q_matches = list(re.finditer(r'(?:^|\n)\s*([1-9]|10)[\.\)]\s*(.*?)(?=(?:^|\n)\s*(?:[1-9]|10)[\.\)]|\Z)', full_text, re.S))
        seen_qn = set()
        unique_matches = []
        for qm in q_matches:
            qn = int(qm.group(1))
            if qn not in seen_qn:
                seen_qn.add(qn)
                unique_matches.append(qm)
                
        print(f'2025 Week {w_num}: found {len(unique_matches)} questions')
        
        for qm in unique_matches:
            qn = int(qm.group(1))
            block = qm.group(2).strip()
            
            # Extract Solution if present (anchored at line start)
            solution = ""
            sol_m = re.search(r'(?:^|\n)\s*(?:Solution|Sol\s*ation)[\s:]*(.*)', block, re.S | re.I)
            if sol_m:
                solution = sol_m.group(1).strip()
                block = block[:sol_m.start()].strip()
                
            # Extract Ans
            ans_m = re.search(r'(?:^|\n)\s*Ans[\.\-\s:=]+(.*)', block, re.I)
            if not ans_m:
                ans_m = re.search(r'\bAns[\.\-\s:=]+(.*)', block, re.I)
                
            raw_ans = ""
            if ans_m:
                raw_ans = ans_m.group(1).strip()
                block = block[:ans_m.start()].strip()
                
            # Extract options: a., b., c., d. or A., B., C., D.
            opt_matches = list(re.finditer(r'(?:^|\n)\s*([A-Ea-e])[\.\)]\s*(.*?)(?=(?:^|\n)\s*[A-Ea-e][\.\)]|\Z)', block, re.S))
            options = []
            if opt_matches:
                q_text = block[:opt_matches[0].start()].strip()
                for om in opt_matches:
                    opt_letter = om.group(1).upper()
                    opt_body = re.sub(r'\s+', ' ', om.group(2)).strip()
                    options.append({'key': opt_letter, 'text': opt_body})
            else:
                q_text = block
                
            q_text = re.sub(r'\s+', ' ', q_text).strip()
            q_text = re.sub(r'[\'’`]', "'", q_text)
            
            # Resolve answer keys
            ans_keys = []
            m_letter = re.match(r'^([A-Ea-e])\b', raw_ans)
            if m_letter:
                ans_keys = [m_letter.group(1).upper()]
            else:
                letter_matches = re.findall(r'\b([A-Ea-e])\b', raw_ans)
                if letter_matches:
                    ans_keys = [letter_matches[0].upper()]
                elif raw_ans and options:
                    raw_clean = raw_ans.lower().strip()
                    for opt in options:
                        if opt['text'].lower() == raw_clean or opt['text'].lower() in raw_clean or raw_clean in opt['text'].lower():
                            ans_keys.append(opt['key'])
                            break
                            
            if options and ans_keys:
                opt_keys = [o['key'] for o in options]
                if ans_keys[0] not in opt_keys:
                    raw_clean = raw_ans.lower().strip()
                    for opt in options:
                        if opt['text'].lower() in raw_clean or raw_clean in opt['text'].lower():
                            ans_keys = [opt['key']]
                            break
                            
            results.append({
                'id': f'2025-w{w_num:02d}-q{qn:02d}',
                'year': '2025',
                'yearLabel': '2025 PYQ',
                'week': w_num,
                'weekLabel': f'Week {w_num}',
                'questionNumber': qn,
                'type': 'MSQ' if len(ans_keys) > 1 else 'MCQ',
                'question': q_text,
                'options': options,
                'answer': ans_keys,
                'raw_ans': raw_ans,
                'explanation': solution,
                'source': 'Psychology-of-learning-assignment-2025.pdf'
            })
            
    print(f'Total 2025 parsed: {len(results)}')
    missing_ans = [r for r in results if not r['answer']]
    print(f'2025 with missing answer: {len(missing_ans)}')
    for ma in missing_ans:
        print(f"  Missing ans: {ma['id']} raw_ans='{ma['raw_ans']}' q='{ma['question'][:60]}...' opts={[o['key']+':'+o['text'] for o in ma['options']]}")
    missing_opts = [r for r in results if len(r['options']) < 2]
    print(f'2025 with < 2 options: {len(missing_opts)}')
    for mo in missing_opts:
        print(f"  Missing opts: {mo['id']} q='{mo['question'][:60]}...'")
    return results

if __name__ == '__main__':
    parse_2025()
