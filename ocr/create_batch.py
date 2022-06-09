from pathlib import Path
import csv
from openpecha.utils import load_yaml
import re

def get_unmade_pecha_ids(pecha_ids):
    unmade_pechas = ""
    yml_path = Path(f"./pecha_ids.yml")
    pecha_dic = load_yaml(yml_path)
    for pecha_id in pecha_ids:
        if pecha_id in pecha_dic.keys():
            continue
        else:
            unmade_pechas += pecha_id + "\n"
    return unmade_pechas

def parse_csv():
    num = 0
    pecha_ids = ""
    batch_num = 1
    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[0:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            pecha_ids += pecha_id + "\n"
            # num += 1
            # if num == 100:
            #    Path(f"./ocr-batches/Batch-{batch_num}.txt").write_text(pecha_ids, encoding='utf-8')
            #    batch_num += 1
            #    num = 0
            #    pecha_ids = ""
    return pecha_ids
               

if __name__ == "__main__":
    pecha_ids = (parse_csv()).splitlines()
    unmade_pecha_ids = get_unmade_pecha_ids(pecha_ids)
    Path(f"./unmade_pechas.txt").write_text(unmade_pecha_ids, encoding='utf-8')    