import nltk
from utils import clear_phrase

with open('dialogues.txt', encoding='utf-8') as f:
    raw = f.read().split('\n\n')
    pairs = [d.split('\n')[:2] for d in raw if len(d.split('\n')) >= 2]

cleaned_pairs = []
for q, a in pairs:
    q = clear_phrase(q[2:])
    if q:
        cleaned_pairs.append((q, a[2:]))

def generate_answer(replica):
    replica = clear_phrase(replica)
    answers = []
    for q, a in cleaned_pairs:
        if abs(len(replica) - len(q)) / len(q) < 0.3:
            dist = nltk.edit_distance(replica, q)
            if dist / len(q) < 0.3:
                answers.append((dist, a))
    if answers:
        return sorted(answers)[0][1]
