import time
import json
import shutil
import logging
from git import Repo
from pathlib import Path
from github import Github
from urllib.request import urlopen
from openpecha.utils import load_yaml


url = "https://raw.githubusercontent.com/OpenPecha-dev/editable-text/main/t_text_list.json"
response = urlopen(url)
t_text_list_dictionary = json.loads(response.read())




def get_new_json(ids, text_list):
    final = {}
    curr = {}
    for text_id, info in t_text_list_dictionary.items():
        if text_id in text_list:
            continue
        else:
            old_google = t_text_list_dictionary[text_id]['google']
            old_namsel = t_text_list_dictionary[text_id]['namsel']
            title = t_text_list_dictionary[text_id]['title']
            new_google = ids[old_google]
            new_namsel = ids[old_namsel]
            curr[text_id]= {
                'google': new_google,
                'namsel': new_namsel,
                'title': title
            }
            final.update(curr)
            curr = {}
    return final



if __name__ == "__main__":
    ids = load_yaml(Path(f"./ids.yml"))
    text_list = (Path(f"./text_list.txt").read_text(encoding='utf-8')).splitlines()
    new_json = get_new_json(ids, text_list)
    final_json = json.dumps(new_json, sort_keys=True, ensure_ascii=False)
    Path(f"./new_json2.json").write_text(final_json, encoding="utf-8")


