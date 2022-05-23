from __future__ import annotations
from pathlib import Path 
from openpecha.utils import dump_yaml, load_yaml


def update_index_base(pecha_path, base_dic):
    index_path = ""
    index = dump_yaml(index_path)
    annotations = index['annotations']
    for _, base_info in base_dic.items():
        for _, ann_info in annotations.items():
            if int(base_info['old_base'][1:]) == ann_info['span'][0]['vol']:
                start = ann_info['span']['start']
                end = ann_info['span']['end']
                del ann_info['span'][0]['vol']
                ann_info['span']={
                }



if __name__ =="__main__":
    pecha_path = ""
    update_index_base(pecha_path)