from pathlib import Path
import yaml



def write_yaml(dic):
    yml = yaml.safe_dump(dic, sort_keys=True)
    Path(f'./pecha_dic.yml').write_text(yml, encoding='utf-8')




if __name__ == "__main__":
    dic = yaml.safe_load(Path(f"./ocr/pecha_ids.yml").read_text(encoding='utf-8'))
    write_yaml(dic)