import json

with open('streamerlist.json', 'r') as f:
    data = json.load(f)

print(data['diskdur'])