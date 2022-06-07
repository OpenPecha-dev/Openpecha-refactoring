from pathlib import Path
import csv
import re


def parse_csv():
    num = 0
    pecha_ids = ""
    batch_num = 1
    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[0:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            pecha_ids += pecha_id + "\n"
            num += 1
            if num == 100:
               Path(f"./ocr-batches/Batch-{batch_num}.txt").write_text(pecha_ids, encoding='utf-8')
               batch_num += 1
               num = 0
               pecha_ids = ""
               
               
if __name__ == "__main__":
    parse_csv()
               