import json
with open('data/questions.json') as f:
    data = json.load(f)
print('✓ JSON is valid\n')
print(f'Question Banks ({len(data["banks"])} total):')
for bank in data['banks']:
    print(f'  • {bank["key"]}: {bank["label"]} ({len(bank["questions"])} questions)')
