import fitz
import re

doc2025 = fitz.open('Extras/Psychology-of-learning-assignment-2025.pdf')
text2025 = '\n'.join(p.get_text() for p in doc2025)

doc2024 = fitz.open('Extras/Psycology of lerning 2024.pdf')
text2024 = '\n'.join(p.get_text() for p in doc2024)

targets_2025 = [
    'Smiling and complimenting',
    'create a new memory',
    'According to the neural network model',
    'A mental representation can take',
    'Cognitive architecture is a theory',
    'knowledge refers to knowledge of terminology',
    'ability to regulate your thoughts',
    'Reflection, learning and education',
    'In ADDIE model',
    'learners are the makers of meaning',
    'experiential learning style theory',
    'places the firmly at the center'
]

print("=== 2025 TARGETS ===")
for t in targets_2025:
    pos = text2025.find(t)
    if pos != -1:
        print(f"--- MATCH: {t} ---")
        print(text2025[pos-30:pos+350])
        print("="*40)
    else:
        print(f"--- NOT FOUND: {t} ---")

print("\n=== 2024 TARGETS ===")
targets_2024 = [
    'EI can be developed at any stage',
    'type of e-learning is highly interactive'
]
for t in targets_2024:
    pos = text2024.find(t)
    if pos != -1:
        print(f"--- MATCH: {t} ---")
        print(text2024[pos-30:pos+350])
        print("="*40)
    else:
        print(f"--- NOT FOUND: {t} ---")
