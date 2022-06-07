
import subprocess
from github import Github
from pathlib import Path
from openpecha.utils import load_yaml, dump_yaml
from pipeline import clean_dir, download_pecha, push_changes


def get_commits(pecha_path, token):
    pecha_id = pecha_path.name
    g = Github(token)
    repo = g.get_repo(f"Openpecha/{pecha_id}")
    for num, commit in enumerate(repo.get_commits(), 1):
        if num == 1:
            last_commit = commit._identity
        if num == 2:
            second_last_commit = commit._identity
    return last_commit, second_last_commit


def update_meta(source_metadata, meta_path):
    meta = load_yaml(meta_path)
    meta['source_metadata'] = source_metadata
    dump_yaml(meta, meta_path)

def get_new_source_metadata(source_metadata, base_list):
    base = {}
    curr = {}
    volumes = source_metadata['volumes']
    del source_metadata['volumes']
    if len(base_list) == 1:
        for _, volume_info in volumes.items():
            new_base = base_list[0]
            curr = {
                'image_group_id': volume_info.get('image_group_id', ''),
                'title': volume_info.get('title', ''),
                'total_pages':  volume_info.get('total_pages', ''),
                'order':  volume_info.get('volume_number', ''),
                'base_file': f'{new_base}.txt' 
            }
            base[new_base]= curr
            curr ={}
            break
        source_metadata['base'] = base
    return source_metadata


def get_base_names(pecha_path):
    base_names = []
    layer_paths = Path(f"{pecha_path}/{pecha_path.name}.opf/layers/").iterdir()
    for layer_path in layer_paths:
        base_names.append(layer_path.name)
    return base_names


def get_old_source_metadata(pecha_path, old_pecha_id, token):
    last_commit, second_last_commit = get_commits(pecha_path, token)
    subprocess.run(f'cd {pecha_path};git reset --hard {second_last_commit};', shell=True)
    meta = load_yaml(Path(f"{pecha_path}/{old_pecha_id}.opf/meta.yml"))
    old_source_metadata = meta['source_metadata']
    subprocess.run(f'cd {pecha_path};git reset --hard {last_commit};', shell=True)
    return old_source_metadata


def check_base_of_opf(pecha_path, old_pecha_id, commit_msg, token):
    meta_path = Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml")
    meta = load_yaml(meta_path)
    source_metadata = meta['source_metadata']
    base = source_metadata['base']
    if base == {}:
        old_source_metadata = get_old_source_metadata(pecha_path, old_pecha_id, token)
        base_names = get_base_names(pecha_path)
        new_source_metadata = get_new_source_metadata(old_source_metadata, base_names)
        update_meta(new_source_metadata, meta_path)
        push_changes(pecha_path, commit_msg, token)
        print(f"updated {new_id} base")
        
        
        
        
if __name__ == "__main__":
    token = "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"
    commit_msg = "added the base in the meta"
    ids = load_yaml(Path(f"./ids.yml"))
    output_path = Path(f"./pechas")
    for old_id, new_id in ids.items():
        if len(old_id) > 9:
            pecha_path = download_pecha(new_id, output_path)
            check_base_of_opf(pecha_path, old_id, commit_msg, token)
            clean_dir(pecha_path)
            