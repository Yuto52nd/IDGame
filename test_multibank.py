from app import app, rooms
from question_store import get_questions_from_banks

client = app.test_client()
response = client.post('/create', data={'name': 'Host', 'question_banks': ['spicy', 'general']})
room = next(iter(rooms.values()))
combined = get_questions_from_banks(room['question_banks'])

print('Testing multi-bank question selection:')
print(f'  Room question banks: {room["question_banks"]}')
print(f'  Combined pool size: {len(combined)} questions')
assert 'spicy' in room['question_banks'] and 'general' in room['question_banks']
assert len(combined) == 128 + 70
print('✓ Multi-bank selection working correctly')

# Test with single bank
rooms.clear()
response = client.post('/create', data={'name': 'Host2', 'question_banks': ['classic']})
room2 = next(iter(rooms.values()))
pool2 = get_questions_from_banks(room2['question_banks'])
print(f'  Single bank (classic): {len(pool2)} questions')
assert len(pool2) == 21
print('✓ Single-bank fallback working')

# Test with default (no selection)
rooms.clear()
response = client.post('/create', data={'name': 'Host3'})
room3 = next(iter(rooms.values()))
print(f'  Default selection: {room3["question_banks"]}')
assert room3['question_banks'] == ['classic']
print('✓ Default fallback working')
