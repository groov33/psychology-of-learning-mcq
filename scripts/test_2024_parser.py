import fitz
import re
import os

def parse_2024():
    doc = fitz.open('Extras/Psycology of lerning 2024.pdf')
    
    page_texts = []
    current_week = 0
    for p_no in range(len(doc)):
        p_text = doc[p_no].get_text()
        m = re.search(r'July\s+2024[-–—\s]+(\d+)\s+Assignment', p_text, re.I)
        if m:
            current_week = int(m.group(1))
        page_texts.append((p_no + 1, current_week, p_text))
    doc.close()
    
    weeks_dict = {}
    for p_no, w_num, txt in page_texts:
        if w_num not in weeks_dict:
            weeks_dict[w_num] = []
        weeks_dict[w_num].append((p_no, txt))
        
    results = []
    for w_num in sorted(weeks_dict.keys()):
        pages_content = [t for _, t in weeks_dict[w_num]]
        week_text = '\n'.join(pages_content)
        
        # Pre-clean known NPTEL OCR / PDF layout collisions
        # Fix Week 5 Q7: "7re)wVarledn. ce, or the perceived value of reward"
        week_text = re.sub(r'7re\)wVarledn\.\s*ce,\s*or\s*the\s*perceived\s*value\s*of\s*reward,\s*would\s*have', 
                           '7) Valence, or the perceived value of reward, would have', week_text)
        
        # Clean header and footer lines
        cleaned_lines = []
        for line in week_text.splitlines():
            line_s = line.strip()
            if any(h in line_s for h in [
                'NPTEL Online Certification Courses',
                'Indian Institute of Technology Kharagpur',
                'Psychology of Learning',
                'TYPE OF QUESTION:',
                'Number of questions:'
            ]):
                continue
            if re.match(r'^July\s+2024[-–—\s]+\d+\s+Assignment', line_s, re.I):
                continue
            cleaned_lines.append(line)
        cleaned_text = '\n'.join(cleaned_lines)
        
        # If Week 4, the second "6)" is actually question 7 ("Which of the following is not an effective way to develop reflective thinking?")
        if w_num == 4:
            cleaned_text = re.sub(r'(\n\s*)6\)\s*(Which of the following is not an effective way to develop reflective thinking)', r'\1 7) \2', cleaned_text)
            
        # Split by question numbers: 1) to 10)
        # Note: some questions have "QUESTION X:" followed by "X)" or just "X)"
        q_matches = list(re.finditer(r'(?:QUESTION\s*(\d+)[:\s]*|^\s*(\d+)[\.\)]\s*)', cleaned_text, re.M | re.I))
        seen_q = set()
        q_indices = []
        for m in q_matches:
            qn = int(m.group(1) or m.group(2))
            # Ignore trailing misplaced QUESTION labels at the bottom of pages
            if qn not in seen_q and 1 <= qn <= 10:
                seen_q.add(qn)
                q_indices.append((qn, m.start()))
                
        q_indices.sort(key=lambda x: x[1])
        
        for idx in range(len(q_indices)):
            qn, start_pos = q_indices[idx]
            end_pos = q_indices[idx+1][1] if idx + 1 < len(q_indices) else len(cleaned_text)
            block = cleaned_text[start_pos:end_pos].strip()
            
            # Remove leading QUESTION X: or X)
            block = re.sub(r'^(?:QUESTION\s*\d+[:\s]*|\d+[\.\)][\s]*)', '', block, flags=re.I).strip()
            block = re.sub(r'^(?:\d+[\.\)][\s]*)', '', block).strip()
            
            # Extract Solution if present
            solution = ""
            sol_m = re.search(r'\bSolution:\s*(.*)', block, re.S | re.I)
            if sol_m:
                solution = sol_m.group(1).strip()
                block = block[:sol_m.start()].strip()
                
            # Extract Answer: using word boundary \bAns
            ans_m = re.search(r'\b(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*(.*)', block, re.I)
            raw_ans = ""
            if ans_m:
                raw_ans = ans_m.group(1).strip()
                block = block[:ans_m.start()].strip()
                
            # Extract Options: A. B. C. D. E.
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
                
            # Clean up trailing "QUESTION \d+:" in options or text if page footer leaked in
            if options:
                options[-1]['text'] = re.sub(r'\s*QUESTION\s*\d+[:\s]*$', '', options[-1]['text'], flags=re.I).strip()
                options[-1]['text'] = re.sub(r'\*+END\*+', '', options[-1]['text']).strip()
                
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
            
            results.append({
                'id': f'2024-w{w_num:02d}-q{qn:02d}',
                'year': '2024',
                'yearLabel': '2024 PYQ',
                'week': w_num,
                'weekLabel': f'Week {w_num}' if w_num > 0 else 'Week 0 (Intro)',
                'questionNumber': qn,
                'type': 'MSQ' if len(ans_keys) > 1 else 'MCQ',
                'question': q_text,
                'options': options,
                'answer': ans_keys,
                'raw_ans': raw_ans,
                'explanation': solution,
                'source': 'Psycology of lerning 2024.pdf'
            })
            
    print(f'Total 2024 parsed: {len(results)}')
    missing_ans = [r for r in results if not r['answer']]
    print(f'2024 with missing answer: {len(missing_ans)}')
    for ma in missing_ans:
        print(f"  Missing ans: {ma['id']} raw_ans='{ma['raw_ans']}' q='{ma['question'][:60]}...'")
    missing_opts = [r for r in results if len(r['options']) < 2]
    print(f'2024 with < 2 options: {len(missing_opts)}')
    for mo in missing_opts:
        print(f"  Missing opts: {mo['id']} q='{mo['question'][:60]}...'")
    return results

if __name__ == '__main__':
    parse_2024()
