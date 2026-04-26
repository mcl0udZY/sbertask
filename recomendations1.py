import json
from collections import defaultdict, Counter

def train_test_split(sessions):
   
    train_sessions = [session[:-1] for session in sessions]
    test_targets = [session[-1] for session in sessions]
    return train_sessions, test_targets

def hit_at_k(recommendations, true_items, k):
    
    assert len(recommendations) == len(true_items)
    hits = 0

    for recs, true_item in zip(recommendations, true_items):
        if true_item in recs[:k]:
            hits += 1

    return hits / len(true_items)

def count_popular_items(sessions):
    popular_items = Counter()
    for session in sessions:
        for item in session:
            popular_items[item] += 1

    return popular_items

def count_transitions(sessions):
    transitions = defaultdict(Counter)
    for session in sessions:
        for i in range(len(session) - 1):
            current_item = session[i]
            next_item = session[i + 1]
            transitions[current_item][next_item] += 1

    return transitions

def count_associations(sessions):
    associations = defaultdict(Counter)
    for session in sessions:
        unique_items = set(session)

        for item in unique_items:
            for other_item in unique_items:
                if item != other_item:
                    associations[item][other_item] += 1

    return associations

def make_recommendations(train_sessions, k=10):
    popular_items = count_popular_items(train_sessions)
    transitions = count_transitions(train_sessions)
    associations = count_associations(train_sessions)
    recommendations = []
    association_weight = 0.0015
    for session in train_sessions:
        last_item = session[-1]
        scores = Counter()

        for item, count in transitions[last_item].items():
            if item != last_item:
                scores[item] += count

        for session_item in set(session):
            for item, count in associations[session_item].items():
                if item != last_item:
                    scores[item] += count * association_weight

        recs = []

        for item, score in scores.most_common():
            if item != last_item and item not in recs:
                recs.append(item)

            if len(recs) == k:
                break

        for item, count in popular_items.most_common():
            if len(recs) == k:
                break

            if item != last_item and item not in recs:
                recs.append(item)

        recommendations.append(recs)

    return recommendations

sessions = []

with open("sessions.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            session = json.loads(line)

            if len(session) >= 3:
                sessions.append(session)

print(f"Всего сессий: {len(sessions)}")
print(f"Первая сессия: {sessions[0]}")

train_sessions, true_items = train_test_split(sessions)
recommendations = make_recommendations(train_sessions, k=10)
score = hit_at_k(recommendations, true_items, k=10)
print(f"Рез теста: {score}")