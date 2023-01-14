import json

data = json.load(open("./json_data/inandout.json", encoding="utf-8"))
learn_list = json.load(open("./json_data/learn_list.json", encoding="utf-8"))

for key, inandouts in data.items():
    try:
        for input_ in inandouts["inputs"]:
            learn_list[key].append(input_)
    except KeyError:
        learn_list[key] = inandouts["inputs"]

with open("./json_data/learn_list.json", "w", encoding="utf-8") as f:
    json.dump(learn_list,f, indent = 4, ensure_ascii=False,)
# print(learn_list)