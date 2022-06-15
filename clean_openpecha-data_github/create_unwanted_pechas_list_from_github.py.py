import yaml
from pathlib import Path


def write_yml(pecha_dic):
    yml = yaml.safe_dump(pecha_dic,sort_keys=True)
    Path(f"./pecha_dic.yml").write_text(yml, encoding='utf-8')

def create_old_pechas_list(pecha_ids, pecha_dic):
    old_pechas = ""
    for pecha_id in pecha_ids:
        if pecha_id in pecha_dic.keys():
            old_pechas += pecha_id+"\n"
    Path(f"./old_pecha_delete_list.txt").write_text(old_pechas, encoding='utf-8')
    
def create_new_pechas_list(pecha_ids, pecha_dic):
    new_pechas = ""
    for pecha_id in pecha_ids:
        check = False
        if pecha_id[0] == "I":
            for _, new_pecha in pecha_dic.items():
                if pecha_id == new_pecha:
                    check = True
            if check == False:
                new_pechas += pecha_id+"\n"
    Path(f"./new_pecha_delete_list.txt").write_text(new_pechas, encoding='utf-8')


if __name__ == "__main__":
    repo_names = (Path(f"./repo_names.txt").read_text(encoding='utf-8')).splitlines()
    pecha_dic = yaml.safe_load(Path(f'./pecha_dic.yml').read_text(encoding='utf-8'))
    create_old_pechas_list(repo_names, pecha_dic)
    create_new_pechas_list(repo_names, pecha_dic)