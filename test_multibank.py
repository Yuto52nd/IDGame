import json

from app import app, rooms
from app import build_question_options
from question_store import get_questions_from_banks


with open('data/questions.json', encoding='utf-8') as questions_file:
	question_data = json.load(questions_file)

print('Testing question data:')
assert question_data['banks']
assert all(bank['key'] and bank['label'] and bank['questions'] for bank in question_data['banks'])
print('✓ Question data is valid')

options = build_question_options([
	'Question 1',
	'Question 2',
	'Question 3',
	'Question 4',
	'Question 5',
	'Question 6',
], 'Question 6')
assert len(options) == 5
assert 'Question 6' in options
assert len(set(options)) == 5
print('✓ Five-question options working correctly')

client = app.test_client()
response = client.post('/create', data={'name': 'Host', 'question_banks': ['spicy', 'general']})
room = next(iter(rooms.values()))
combined = get_questions_from_banks(room['question_banks'])

print('Testing multi-bank question selection:')
print(f'  Room question banks: {room["question_banks"]}')
print(f'  Combined pool size: {len(combined)} questions')
assert 'spicy' in room['question_banks'] and 'general' in room['question_banks']
assert len(combined) == 193 + 135
print('✓ Multi-bank selection working correctly')

# Test with single bank
rooms.clear()
response = client.post('/create', data={'name': 'Host2', 'question_banks': ['classic']})
room2 = next(iter(rooms.values()))
pool2 = get_questions_from_banks(room2['question_banks'])
print(f'  Single bank (classic): {len(pool2)} questions')
assert len(pool2) == 86
print('✓ Single-bank fallback working')

# Test with default (no selection)
rooms.clear()
response = client.post('/create', data={'name': 'Host3'})
room3 = next(iter(rooms.values()))
print(f'  Default selection: {room3["question_banks"]}')
assert room3['question_banks'] == ['classic']
print('✓ Default fallback working')
