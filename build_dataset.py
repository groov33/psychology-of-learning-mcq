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

def clean_explanation(exp):
    if not exp:
        return ""
    m = re.search(r'(for\s+better\s+under(?:standing|oerstanoing)[\.]?)', exp, re.I)
    if m:
        exp = exp[:m.end()].strip()
    exp = re.sub(r'[\*\s]*END[\*\s]*', '', exp, flags=re.I).strip()
    exp = re.sub(r'QUESTION\s*\d+[:\s]*', '', exp, flags=re.I).strip()
    exp = re.sub(r'\{?[0-9A-Za-z!/|\\\'’\"]{4,20}\s*\d*[:\s]*$', '', exp).strip()
    exp = re.sub(r'Scanned\s*with\s*OKEN\s*Scanner[i]?', '', exp, flags=re.I).strip()
    exp = exp.replace('P1ease', 'Please').replace('unoerstanding', 'understanding').replace('slioe', 'slide')
    exp = exp.replace('week-S', 'week-5').replace('slide no.6B', 'slide no.68').replace('slide no.DB', 'slide no.08')
    exp = re.sub(r'^\.?\s*', '', exp)
    return exp.strip()

def apply_curated_fixes(all_qs):
    for q in all_qs:
        qid = q['id']
        
        # General cleanup of leading numbers in questions
        q['question'] = re.sub(r'^\s*(?:QUESTION\s*\d+[:\s]*|\d+[\.\)][\s]*)', '', q['question'], flags=re.I).strip()
        
        # Explanation cleanup
        if 'explanation' in q:
            q['explanation'] = clean_explanation(q['explanation'])
        
        # Specific Question Refinements
        
        # 2026-w06-q07: NPTEL assignment PDF says "Ans. a= all of the given" but "all of the given" is option D!
        if qid == '2026-w06-q07':
            q['question'] = 'Which of the following is a facilitator of EQ?'
            q['options'] = [
                {'key': 'A', 'text': 'optimism'},
                {'key': 'B', 'text': 'happiness'},
                {'key': 'C', 'text': 'independence'},
                {'key': 'D', 'text': 'all of the given'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-6 (slide no.18) for better understanding. (Note: NPTEL assignment PDF had a typographical error stating "Ans. a=" instead of "Ans. d= all of the given").'
            
        # 2026-w09-q07
        elif qid == '2026-w09-q07':
            q['question'] = 'Learners may multitask when engaging in an online course, which could be resulting in ____.'
            q['options'] = [
                {'key': 'A', 'text': 'hyperfocus'},
                {'key': 'B', 'text': 'better retrieval'},
                {'key': 'C', 'text': 'shorter attention spans'},
                {'key': 'D', 'text': 'None of the given'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-9 (slide no.19) for better understanding.'
            
        # 2025-w01-q05
        elif qid == '2025-w01-q05':
            q['question'] = '"Psychology as the Behaviorist Views It" is the famous work of'
            q['options'] = [
                {'key': 'A', 'text': 'Sigmund Freud'},
                {'key': 'B', 'text': 'John Watson'},
                {'key': 'C', 'text': 'Albert Bandura'},
                {'key': 'D', 'text': 'Ivan Pavlov'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-1 (slide no.08) for better understanding.'
            
        # 2025-w01-q09
        elif qid == '2025-w01-q09':
            q['question'] = 'Students persist in the face of challenging tasks and process information more deeply when they adopt ____ goals.'
            q['options'] = [
                {'key': 'A', 'text': 'performance'},
                {'key': 'B', 'text': 'insignificant'},
                {'key': 'C', 'text': 'mastery'},
                {'key': 'D', 'text': 'repetitive'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-1 (slide no.20) for better understanding.'
            
        # 2025-w02-q08
        elif qid == '2025-w02-q08':
            q['question'] = 'Which of the following psychologists was instrumental in engendering the dramatic shift from behaviorism to cognitive theories?'
            q['options'] = [
                {'key': 'A', 'text': 'Tolman'},
                {'key': 'B', 'text': 'Bruner'},
                {'key': 'C', 'text': 'Gestalt'},
                {'key': 'D', 'text': 'All of the above'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-2 (slide no.39) for better understanding.'
            
        # 2025-w02-q10
        elif qid == '2025-w02-q10':
            q['question'] = 'BBL deals with the concept of learning in a ____ context.'
            q['options'] = [
                {'key': 'A', 'text': 'neuro-physiological'},
                {'key': 'B', 'text': 'cognitive'},
                {'key': 'C', 'text': 'social'},
                {'key': 'D', 'text': 'behavioral'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-2 (slide no.68) for better understanding.'
            
        # 2025-w03-q02
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
            
        # 2025-w03-q06
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
            
        # 2025-w05-q03
        elif qid == '2025-w05-q03':
            q['question'] = 'Which of the following does not come under intrinsic motivation?'
            q['options'] = [
                {'key': 'A', 'text': 'interests'},
                {'key': 'B', 'text': 'social pressure'},
                {'key': 'C', 'text': 'curiosity'},
                {'key': 'D', 'text': 'self-satisfaction'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-5 (slide no.5) for better understanding.'
            
        # 2025-w06-q02
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
            
        # 2025-w07-q02
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
            
        # 2025-w07-q05
        elif qid == '2025-w07-q05':
            q['question'] = '____ gives information to learners about their success or failure concerning the task at hand.'
            q['options'] = [
                {'key': 'A', 'text': 'Cognitive feedback'},
                {'key': 'B', 'text': 'Emotional feedback'},
                {'key': 'C', 'text': 'Reinforcement'},
                {'key': 'D', 'text': 'Physical feedback'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-7 (slide no.07) for better understanding.'

        # 2025-w07-q06
        elif qid == '2025-w07-q06':
            q['question'] = 'The ____ orientation to learning has a quality of personal involvement - the whole person in both feeling and cognitive aspects being in the learning event.'
            q['options'] = [
                {'key': 'A', 'text': 'behavioral'},
                {'key': 'B', 'text': 'cognitive'},
                {'key': 'C', 'text': 'humanistic'},
                {'key': 'D', 'text': 'social'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-7 (slide no.08) for better understanding.'
            
        # 2025-w08-q02
        elif qid == '2025-w08-q02':
            q['question'] = 'Good pedagogy is about'
            q['options'] = [
                {'key': 'A', 'text': 'enabling self to be good at rote memorization'},
                {'key': 'B', 'text': 'eliciting responses that demonstrate understanding'},
                {'key': 'C', 'text': 'hampering cognitive development of learners'},
                {'key': 'D', 'text': 'None of the above'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-8 (slide no.04) for better understanding.'
            
        # 2025-w08-q05
        elif qid == '2025-w08-q05':
            q['question'] = 'Which of the following is false about inquiry-based learning?'
            q['options'] = [
                {'key': 'A', 'text': 'is a form of passive learning'},
                {'key': 'B', 'text': 'includes problem-based learning'},
                {'key': 'C', 'text': 'generally used in small scale investigations'},
                {'key': 'D', 'text': 'starts by posing questions'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-8 (slide no.07) for better understanding.'
            
        # 2025-w08-q10
        elif qid == '2025-w08-q10':
            q['question'] = 'People with ____ learning style are hands-on learners, and rely on intuition over logic.'
            q['options'] = [
                {'key': 'A', 'text': 'converging'},
                {'key': 'B', 'text': 'accommodating'},
                {'key': 'C', 'text': 'integrating'},
                {'key': 'D', 'text': 'emotional'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-8 (slide no.25) for better understanding.'
            
        # 2025-w09-q09
        elif qid == '2025-w09-q09':
            q['question'] = 'Our brain has approximately ____ neurons that send information to one another.'
            q['options'] = [
                {'key': 'A', 'text': '85 billion'},
                {'key': 'B', 'text': '85 million'},
                {'key': 'C', 'text': '85 lakhs'},
                {'key': 'D', 'text': '85,000'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-9 (slide no.15) for better understanding.'
            
        # 2025-w10-q09
        elif qid == '2025-w10-q09':
            q['question'] = 'Which of the following is an example of a reward?'
            q['options'] = [
                {'key': 'A', 'text': 'clapping'},
                {'key': 'B', 'text': 'giving money'},
                {'key': 'C', 'text': 'giving a compliment'},
                {'key': 'D', 'text': 'all of the above'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-10 (slide no.24) for better understanding.'
            
        # 2025-w10-q10
        elif qid == '2025-w10-q10':
            q['question'] = '____ is a teaching approach that generates feedback students can use to improve their performance.'
            q['options'] = [
                {'key': 'A', 'text': 'Assessment for performance'},
                {'key': 'B', 'text': 'Assessment for marks'},
                {'key': 'C', 'text': 'Assessment for rewards'},
                {'key': 'D', 'text': 'Assessment for learning'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-10 (slide no.44) for better understanding.'
            
        # 2025-w11-q01
        elif qid == '2025-w11-q01':
            q['question'] = 'Social cognition is the cognitive processes that influence'
            q['options'] = [
                {'key': 'A', 'text': 'social schema'},
                {'key': 'B', 'text': 'social behavior'},
                {'key': 'C', 'text': 'social media'},
                {'key': 'D', 'text': 'none of the above'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-11 (slide no.02) for better understanding.'
            
        # 2025-w11-q03
        elif qid == '2025-w11-q03':
            q['question'] = 'Which of the following abilities does not come under social cognition?'
            q['options'] = [
                {'key': 'A', 'text': 'rote memory'},
                {'key': 'B', 'text': 'face processing'},
                {'key': 'C', 'text': 'joint attention'},
                {'key': 'D', 'text': 'moral reasoning'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-11 (slide no.03) for better understanding.'

        # 2025-w11-q05: Fixed duplicate option keys (A, B, A, B) -> (A, B, C, D)
        elif qid == '2025-w11-q05':
            q['question'] = "A theory of mind refers to a person's ability to understand and think about the ____ of other people."
            q['options'] = [
                {'key': 'A', 'text': 'biological states'},
                {'key': 'B', 'text': 'mental states'},
                {'key': 'C', 'text': 'physical traits'},
                {'key': 'D', 'text': 'none of the above'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-11 (slide no.08) for better understanding.'
            
        # 2025-w11-q08
        elif qid == '2025-w11-q08':
            q['question'] = 'Children become more aggressive when they observe aggressive or violent models.'
            q['options'] = [
                {'key': 'A', 'text': 'True'},
                {'key': 'B', 'text': 'False'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-11 (slide no.17) for better understanding.'

        # 2025-w11-q09
        elif qid == '2025-w11-q09':
            q['question'] = 'The ____ model of observational learning involves real or fictional characters displaying behaviors in books, films, television programs, or online media.'
            q['options'] = [
                {'key': 'A', 'text': 'symbolic'},
                {'key': 'B', 'text': 'live'},
                {'key': 'C', 'text': 'verbal instructional'},
                {'key': 'D', 'text': 'contextual'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-11 (slide no.17) for better understanding.'

        # 2024-w02-q01
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

        # 2024-w06-q06: Clean True/False question, remove spurious option C
        elif qid == '2024-w06-q06':
            q['question'] = 'EI can be developed at any stage of life through self-effort & training.'
            q['options'] = [
                {'key': 'A', 'text': 'True'},
                {'key': 'B', 'text': 'False'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-6 (slide no.20) for better understanding.'

        # 2024-w09-q02: Option A was swallowed into question text
        elif qid == '2024-w09-q02':
            q['question'] = '____ type of e-learning is highly interactive, which includes graphics, video, audio and games too.'
            q['options'] = [
                {'key': 'A', 'text': 'text driven'},
                {'key': 'B', 'text': 'simulation'},
                {'key': 'C', 'text': 'interactive'},
                {'key': 'D', 'text': 'none of the given'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-9 (slide no.06) for better understanding.'

        # 2025-w02-q07: Option B was merged with Option A in OCR
        elif qid == '2025-w02-q07':
            q['question'] = 'Smiling and complimenting students for good performance is a type of'
            q['options'] = [
                {'key': 'A', 'text': 'negative punishment'},
                {'key': 'B', 'text': 'positive punishment'},
                {'key': 'C', 'text': 'negative reinforcement'},
                {'key': 'D', 'text': 'positive reinforcement'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-2 (slide no.22) for better understanding.'

        # 2025-w03-q03: Option B was merged with Option A in OCR
        elif qid == '2025-w03-q03':
            q['question'] = 'In order to create a new memory, information must be changed into'
            q['options'] = [
                {'key': 'A', 'text': 'a usable form'},
                {'key': 'B', 'text': 'a long form'},
                {'key': 'C', 'text': 'a short form'},
                {'key': 'D', 'text': 'a visual form'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-3 (slide no.03) for better understanding.'

        # 2025-w03-q10: Option A was swallowed into question text in OCR
        elif qid == '2025-w03-q10':
            q['question'] = 'According to the neural network model, memory capacity depends on'
            q['options'] = [
                {'key': 'A', 'text': 'complexity of the synapses'},
                {'key': 'B', 'text': 'sparseness of representations'},
                {'key': 'C', 'text': 'spatial and temporal correlations between memories'},
                {'key': 'D', 'text': 'all of the above'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-3 (slide no.41) for better understanding.'

        # 2025-w04-q03: Option B was merged with Option A in OCR
        elif qid == '2025-w04-q03':
            q['question'] = 'A mental representation can take the form of a'
            q['options'] = [
                {'key': 'A', 'text': 'word'},
                {'key': 'B', 'text': 'image'},
                {'key': 'C', 'text': 'sound'},
                {'key': 'D', 'text': 'all of the given'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-4 (slide no.05) for better understanding.'

        # 2025-w04-q05: Option B was merged with Option A in OCR
        elif qid == '2025-w04-q05':
            q['question'] = 'Cognitive architecture is a theory about the ____ that create a mind in natural or artificial systems.'
            q['options'] = [
                {'key': 'A', 'text': 'structures'},
                {'key': 'B', 'text': 'facts'},
                {'key': 'C', 'text': 'images'},
                {'key': 'D', 'text': 'sounds'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-4 (slide no.11) for better understanding.'

        # 2025-w04-q07: Option B was merged with Option A in OCR
        elif qid == '2025-w04-q07':
            q['question'] = '____ knowledge refers to knowledge of terminology and specific details.'
            q['options'] = [
                {'key': 'A', 'text': 'Metacognitive'},
                {'key': 'B', 'text': 'Conceptual'},
                {'key': 'C', 'text': 'Kinesthetic'},
                {'key': 'D', 'text': 'Factual'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-4 (slide no.19) for better understanding.'

        # 2025-w04-q09: OCR line break in Option D
        elif qid == '2025-w04-q09':
            q['question'] = '____ refers to the ability to regulate your thoughts and set aside any personal biases to come to the best conclusion.'
            q['options'] = [
                {'key': 'A', 'text': 'Self-regulation'},
                {'key': 'B', 'text': 'Openmindedness'},
                {'key': 'C', 'text': 'Observation'},
                {'key': 'D', 'text': 'Interpretation'},
                {'key': 'E', 'text': 'Elaboration'}
            ]
            q['answer'] = ['A']
            q['explanation'] = 'Please go through lecture notes of week-4 (slide no.32) for better understanding.'

        # 2025-w07-q03: Option B was merged with Option A in OCR
        elif qid == '2025-w07-q03':
            q['question'] = 'Reflection, learning and education was explored by'
            q['options'] = [
                {'key': 'A', 'text': 'Carl Rogers'},
                {'key': 'B', 'text': 'John Watson'},
                {'key': 'C', 'text': 'Benjamin Bloom'},
                {'key': 'D', 'text': 'John Dewey'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-7 (slide no.05) for better understanding.'

        # 2025-w07-q10: Option A swallowed in question text in OCR
        elif qid == '2025-w07-q10':
            q['question'] = 'In ADDIE model, I stands for'
            q['options'] = [
                {'key': 'A', 'text': 'instruction'},
                {'key': 'B', 'text': 'implementation'},
                {'key': 'C', 'text': 'integration'},
                {'key': 'D', 'text': 'induction'}
            ]
            q['answer'] = ['B']
            q['explanation'] = 'Please go through lecture notes of week-7 (slide no.33) for better understanding.'

        # 2025-w08-q04: Option D was merged with Option C in OCR
        elif qid == '2025-w08-q04':
            q['question'] = 'According to the constructivist approach, learners are the makers of meaning and knowledge.'
            q['options'] = [
                {'key': 'A', 'text': 'solitary learning'},
                {'key': 'B', 'text': 'passive learning'},
                {'key': 'C', 'text': 'constructivist learning'},
                {'key': 'D', 'text': 'metalearning'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-8 (slide no.06) for better understanding.'

        # 2025-w08-q09: Option B merged with Option A; missing answer set to C
        elif qid == '2025-w08-q09':
            q['question'] = "Kolb's experiential learning style theory is typically represented by a ____-stage learning cycle"
            q['options'] = [
                {'key': 'A', 'text': 'three'},
                {'key': 'B', 'text': 'five'},
                {'key': 'C', 'text': 'four'},
                {'key': 'D', 'text': 'seven'}
            ]
            q['answer'] = ['C']
            q['explanation'] = 'Please go through lecture notes of week-8 (slide no.19) for better understanding.'

        # 2025-w09-q05: Option B merged with Option A; OCR typos fixed
        elif qid == '2025-w09-q05':
            q['question'] = 'Recent thinking in cognitive psychology places the ____ firmly at the center of the learning experience.'
            q['options'] = [
                {'key': 'A', 'text': 'computer'},
                {'key': 'B', 'text': 'parent'},
                {'key': 'C', 'text': 'teacher'},
                {'key': 'D', 'text': 'individual'}
            ]
            q['answer'] = ['D']
            q['explanation'] = 'Please go through lecture notes of week-9 (slide no.10) for better understanding.'

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
            
    # Apply precise curated fixes & cleanups
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
