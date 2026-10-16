import glob
import fitz
import json
import re
import os

def parse_nptel_folder():
    files = sorted(glob.glob('Extras/Psychology of learning NPTEL/*.pdf'))
    results = []
    
    for f in files:
        doc = fitz.open(f)
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()
        
        # Determine week number from filename e.g. 01.Assignement_Psy.pdf -> 1
        bname = os.path.basename(f)
        m_week = re.search(r'(\d+)', bname)
        week_num = int(m_week.group(1)) if m_week else 1
        
        # Clean text
        lines = full_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line_str = line.strip()
            # Skip page headers
            if any(h in line_str for h in [
                'NPTEL Online Certification Courses',
                'Indian Institute of Technology Kharagpur',
                'Psychology of Learning',
                'TYPE OF QUESTION:',
                'Number of questions:'
            ]):
                continue
            if re.match(r'^July\s+202[0-9].*?Assignment', line_str, re.I):
                continue
            if re.match(r'^_{5,}', line_str):
                continue
            cleaned_lines.append(line)
            
        full_clean = '\n'.join(cleaned_lines)
        
        # Split into questions by number at start of line: "1)", "2)", ... "10)"
        # Note: some have "QUESTION 1:" before "1)"
        q_blocks = list(re.finditer(r'(?:^|\n)\s*(?:QUESTION\s*\d+[:\s]*)?\s*(\d+)[\.\)]\s*(.*?)(?=(?:^|\n)\s*(?:QUESTION\s*\d+[:\s]*)?\s*\d+[\.\)]|\Z)', full_clean, re.S))
        print(f'{bname} (Week {week_num}): found {len(q_blocks)} blocks')
        
        for q_idx, q_match in enumerate(q_blocks):
            q_num = int(q_match.group(1))
            block_text = q_match.group(2).strip()
            
            # Extract Solution if present
            solution = ""
            sol_m = re.search(r'Solution:\s*(.*)', block_text, re.S | re.I)
            if sol_m:
                solution = sol_m.group(1).strip()
                block_text = block_text[:sol_m.start()].strip()
                
            # Extract Answer
            ans_m = re.search(r'(?:Ans[\.\s:=]+|Answer[\.\s:=]+)\s*([A-Za-z0-9,\s=]+)', block_text, re.I)
            raw_ans = ""
            if ans_m:
                raw_ans = ans_m.group(1).strip()
                block_text = block_text[:ans_m.start()].strip()
                
            # Parse Options (A., B., C., D., E.) or (a., b., c., d., e.)
            # Match options
            opt_matches = list(re.finditer(r'(?:^|\n)\s*([A-Ea-e])[\.\)]\s*(.*?)(?=(?:^|\n)\s*[A-Ea-e][\.\)]|\Z)', block_text, re.S))
            
            if opt_matches:
                question_text = block_text[:opt_matches[0].start()].strip()
                options = []
                for om in opt_matches:
                    opt_letter = om.group(1).upper()
                    opt_text = re.sub(r'\s+', ' ', om.group(2)).strip()
                    options.append({'key': opt_letter, 'text': opt_text})
            else:
                question_text = block_text
                options = []
                
            # Clean answer
            # e.g. "C= Classical conditioning" or "a= all of the given"
            ans_keys = []
            if '=' in raw_ans:
                ans_text = raw_ans.split('=', 1)[1].strip()
                for opt in options:
                    if opt['text'].lower().strip() == ans_text.lower().strip():
                        ans_keys = [opt['key']]
                        break
            if not ans_keys:
                letter_matches = re.findall(r'\b([A-Ea-e])\b', raw_ans)
                if letter_matches:
                    ans_keys = [l.upper() for l in letter_matches]
                elif raw_ans:
                    for opt in options:
                        if opt['text'].lower() in raw_ans.lower() or raw_ans.lower() in opt['text'].lower():
                            ans_keys.append(opt['key'])
                            break
                        
            # Normalize question text
            question_text = re.sub(r'^\s*QUESTION\s*\d+[:\s]*', '', question_text, flags=re.I).strip()
            question_text = re.sub(r'\s+', ' ', question_text).strip()
            
            # Determine type
            q_type = "MSQ" if len(ans_keys) > 1 else "MCQ"
            
            results.append({
                'id': f'2026-w{week_num:02d}-q{q_num:02d}',
                'year': '2026',
                'yearLabel': '2026 (Current)',
                'week': week_num,
                'weekLabel': f'Week {week_num}',
                'questionNumber': q_num,
                'type': q_type,
                'question': question_text,
                'options': options,
                'answer': ans_keys,
                'explanation': solution,
                'source': f'Psychology of learning NPTEL/{bname}'
            })
            
    print(f'Total NPTEL parsed: {len(results)}')
    missing_ans = [r for r in results if not r['answer']]
    print(f'NPTEL with missing answer: {len(missing_ans)}')
    missing_opts = [r for r in results if len(r['options']) < 2]
    print(f'NPTEL with < 2 options: {len(missing_opts)}')
    return results

if __name__ == '__main__':
    parse_nptel_folder()
