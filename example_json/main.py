import json

data = {}
data['people'] = []
data['people'].append({
    'name': 'Scott',
    'website': 'stackabuse.com',
    'from': 'Nebraska'
})
data['people'].append({
    'name': 'Larry',
    'website': 'google.com',
    'from': 'Michigan'
})
data['people'].append({
    'name': 'Tim',
    'website': 'apple.com',
    'from': 'Alabama'
})

f = open("./setting.json", 'w')
json.dump(data, f, ensure_ascii=True, indent=4)
f.close()

with open("./setting.json", 'r') as json_file:
    data = json.load(json_file)
    print(data)
    print(data['people'][0])