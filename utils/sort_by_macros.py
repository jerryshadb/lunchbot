'''
Implement an API call to some LLM to rank menus by how healthy they are. ChatGPT is paid so that's no go
'''


import json
with open ('config.json', 'r') as f:
    config = json.load(f)


def get_macro_weights():
    pass
