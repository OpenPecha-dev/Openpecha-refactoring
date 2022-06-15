from __future__ import annotations
import re
import json
import random
import subprocess
from uuid import uuid4
from pathlib import Path
from github import Github
from datetime import datetime, timezone
from openpecha.utils import load_yaml, dump_yaml
from openpecha.core.metadata import InitialCreationType, InitialPechaMetadata
from openpecha.core.ids import get_base_id



def get_initial_date(pecha_path, token):
    pecha_id = pecha_path.name
    g = Github(token)
    repo = g.get_repo(f"Openpecha-Data/{pecha_id}")
    for commit in repo.get_commits():
        pass
    import_date = commit.raw_data['commit']['author']['date']
    return import_date


def get_new_source_metadata(meta, base_dic):
    base = {}
    curr = {}
    source_metadata = meta['source_metadata']
    if source_metadata.get("volumes", None) != None:
        volumes = source_metadata['volumes']
        del source_metadata['volumes']
    else:
        volumes = source_metadata['volume']
        del source_metadata['volume']
    for _, base_info in base_dic.items():
        old_base = base_info['old_base']
        for _, volume_info in volumes.items():
            if old_base == volume_info['base_file'][:-4]:
                new_base = base_info['new_base']
                curr = {
                    'image_group_id': volume_info.get('image_group_id', ''),
                    'title': volume_info.get('title', ''),
                    'total_pages':  volume_info.get('total_pages', ''),
                    'order':  int(volume_info['base_file'][1:-4]),
                    'base_file': f'{new_base}.txt' 
                }
                base[new_base]= curr
                curr ={}
                break
        source_metadata['base'] = base
    return source_metadata


def update_meta(pecha_path, base_dic, parser, token):
    pecha_id = pecha_path.name
    meta_path = Path(f"{pecha_path}/{pecha_id}.opf/meta.yml")
    meta = load_yaml(meta_path)
    source_metadata = get_new_source_metadata(meta, base_dic)
    new_meta = InitialPechaMetadata(
        source='https://library.bdrc.io',
        initial_creation_type=InitialCreationType.ocr,
        imported=get_initial_date(pecha_path, token),
        last_modified=datetime.now(timezone.utc),
        parser=parser,
        copyright=None,
        license=None,
        source_metadata=source_metadata
    )
    dump_yaml(json.loads(new_meta.json()), meta_path)


def rename_layers(layers_paths, base_dic):
    layers_paths.sort()
    for layer_path in layers_paths:
        layer_name = layer_path.name
        for _, info in base_dic.items():
            if layer_name == info['old_base']:
                new_base = info['new_base']
                break
        subprocess.run(f'cd {layer_path.parent}; git mv {layer_path.name} {new_base}', shell=True)


def rename_all_base(base_paths):
    curr ={}
    base_dic = {}
    base_paths.sort()
    for num, base_path in enumerate(base_paths,0):
        base_name = base_path.name[:-4]
        new_base_name = get_base_id()
        subprocess.run(f'cd {base_path.parent}; git mv {base_path.name} {new_base_name}.txt', shell=True)
        curr[num] = {
            'old_base': base_name,
            'new_base': new_base_name
        }
        base_dic.update(curr)
        curr = {}
    return base_dic


def update_base_and_layer_name(pecha_path):
    pecha_id = pecha_path.name
    base_paths = list(Path(f"{pecha_path}/{pecha_id}.opf/base/").iterdir())
    layers_paths = list(Path(f"{pecha_path}/{pecha_id}.opf/layers/").iterdir())
    base_dic = rename_all_base(base_paths)
    rename_layers(layers_paths, base_dic)
    return base_dic



    