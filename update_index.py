from __future__ import annotations
from pathlib import Path 
from openpecha.utils import dump_yaml, load_yaml


def update_index_base(pecha_path, base_dic):
    index_path = Path(f"{pecha_path}/{pecha_path.name}.opf/index.yml")
    index = load_yaml(index_path)
    annotations = index['annotations']
    for _, base_info in base_dic.items():
        for _, ann_info in annotations.items():
            if int(base_info['old_base'][1:]) == ann_info['span'][0]['vol']:
                base = base_info['new_base']
                start = ann_info['span'][0]['start']
                end = ann_info['span'][0]['end']
                del ann_info['span']
                span = [
                    {
                        'base': base,
                        'start': start,
                        'end': end
                        }
                ]
                ann_info['span']= span
    index['annotations'].update(annotations)
    dump_yaml(index, index_path)



if __name__ =="__main__":
    pecha_path = ""
    update_index_base(pecha_path)