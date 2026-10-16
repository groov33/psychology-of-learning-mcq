import fitz
import re

def parse_2023():
    doc = fitz.open('Extras/Psychology-of-learning-assignments-2023.pdf')
    
    assignments = [
        (0, "Week 0 (Intro)", 1, 3),
        (1, "Week 1", 4, 6),
        (2, "Week 2", 7, 9),
        (3, "Week 3", 10, 12),
        (4, "Week 4", 13, 15),
        (5, "Week 5", 16, 18),
        (6, "Week 6", 19, 21),
        (7, "Week 7", 22, 24),
        (8, "Week 8", 25, 27),
        (9, "Week 9", 28, 30),
        (10, "Week 10", 31, 33),
        (11, "Week 11", 34, 36),
        (12, "Week 12", 37, 39)
    ]
    
    results = []
    
    for w_num, w_label, start_p, end_p in assignments:
        text_parts = []
        for p in range(start_p - 1, end_p):
            t = doc[p].get_text()
            lines = t.splitlines()
            cleaned_lines = []
            for l in lines:
                ls = l.strip()
                if re.match(r'^\d+$', ls) and len(ls) <= 2:
                    continue
                if re.match(r'^(?:NPTEL[\s\-]*)?(?:Zero|Week\s*[-–—:]*\s*\d+)\s+assignment', ls, re.I):
                    continue
                if re.match(r'^Psychology\s*of\s*Learning', ls, re.I):
                    continue
                cleaned_lines.append(l)
            text_parts.append('\n'.join(cleaned_lines))
            
        full_text = '\n'.join(text_parts)
        
        # Pre-process: if "Ans. = X" or "Ans.= X" is embedded at the end of a line, make sure newline precedes it
        full_text = re.sub(r'([^\n])\s+(\bAns[\.\s:=]+[A-Ea-e]\.?)', r'\1\n\2', full_text)
        
        # Questions start with 1) to 12) only (avoids year numbers like 1987.)
        q_matches = list(re.finditer(r'(?:^|\n)\s*([1-9]|1[0-2])[\.\)]\s*(.*?)(?=(?:^|\n)\s*(?:[1-9]|1[0-2])[\.\)]|\Z)', full_text, re.S))
        
        for qm in q_matches:
            qn = int(qm.group(1))
            block = qm.group(2).strip()
            
            # Extract Solution if present
            solution = ""
            sol_m = re.search(r'\bSolution:\s*(.*)', block, re.S | re.I)
            if sol_m:
                solution = sol_m.group(1).strip()
                block = block[:sol_m.start()].strip()
                
            # Extract Ans: look specifically for Ans. = or Ans = or Answer:
            ans_m = re.search(r'(?:^|\n)\s*(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*(.*)', block, re.I)
            if not ans_m:
                ans_m = re.search(r'\bAns[\.\s:=]+([A-Ea-e]\b.*)', block, re.I)
            raw_ans = ""
            if ans_m:
                raw_ans = ans_m.group(1).strip()
                block = block[:ans_m.start()].strip()
                
            # Extract options: a., b., c., d., e. or A., B., C., D., E.
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
                
            # Resolve answer keys
            ans_keys = []
            m_letter = re.match(r'^([A-Ea-e])\b', raw_ans)
            if m_letter:
                ans_keys = [m_letter.group(1).upper()]
            else:
                letter_matches = re.findall(r'\b([A-Ea-e])\b', raw_ans)
                if letter_matches:
                    ans_keys = [l.upper() for l in letter_matches]
                elif raw_ans and options:
                    raw_clean = raw_ans.lower().strip()
                    for opt in options:
                        if opt['text'].lower() == raw_clean or opt['text'].lower() in raw_clean or raw_clean in opt['text'].lower():
                            ans_keys.append(opt['key'])
                            break
                            
            q_text = re.sub(r'\s+', ' ', q_text).strip()
            q_text = re.sub(r'\s*([_\-]{3,})\s*', ' ____ ', q_text)
            
            results.append({
                'id': f'2023-w{w_num:02d}-q{qn:02d}',
                'year': '2023',
                'yearLabel': '2023 PYQ',
                'week': w_num,
                'weekLabel': w_label,
                'questionNumber': qn,
                'type': 'MSQ' if len(ans_keys) > 1 else 'MCQ',
                'question': q_text,
                'options': options,
                'answer': ans_keys,
                'raw_ans': raw_ans,
                'explanation': solution,
                'source': 'Psychology-of-learning-assignments-2023.pdf'
            })
            
    print(f'Total 2023 parsed: {len(results)}')
    missing_ans = [r for r in results if not r['answer']]
    print(f'2023 with missing answer: {len(missing_ans)}')
    for ma in missing_ans:
        print(f"  Missing ans: {ma['id']} raw_ans='{ma['raw_ans']}' q='{ma['question'][:60]}...' opts={[o['key']+':'+o['text'] for o in ma['options']]}")
    missing_opts = [r for r in results if len(r['options']) < 2]
    print(f'2023 with < 2 options: {len(missing_opts)}')
    for mo in missing_opts:
        print(f"  Missing opts: {mo['id']} q='{mo['question'][:60]}...'")
    return results

if __name__ == '__main__':
    parse_2023()
