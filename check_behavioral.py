import json
d = json.load(open('/home/mayu/.nanobot/workspace/interview-prep/data/behavioral.json'))
comps = d['behavioral']['competencies']
first_comp = list(comps.keys())[0]
first_q = comps[first_comp]['questions'][0]
print('type:', type(first_q).__name__)
print('value:', repr(first_q)[:300])
print()
print('all keys if dict:', list(first_q.keys()) if isinstance(first_q, dict) else 'N/A')
