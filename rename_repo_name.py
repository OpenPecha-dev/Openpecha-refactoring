import os
import subprocess
from pathlib import Path
from openpecha import *
from openpecha.utils import load_yaml, dump_yaml
from openpecha.github_utils import create_github_repo



def rename_repo(new_pecha_id, pecha_path, token):
    new_pecha_path = Path(f"./new_opf/{new_pecha_id}")
    os.mkdir(new_pecha_path)
    org = "Openpecha"
    remote_repo_url = create_github_repo(new_pecha_path, org, token)
    subprocess.run(f'cd {pecha_path}; git remote set-url origin {remote_repo_url}',shell=True)


def update_readme(new_pecha_id, pecha_path):
    pecha_id = pecha_path.name
    readme_path = Path(f"{pecha_path}/README.md")
    if readme_path.exists():
        readme = readme_path.read_text(encoding='utf-8')
        new_readme = readme.replace(pecha_id, new_pecha_id)
        readme_path.write_text(new_readme, encoding='utf-8')


def rename_meta(new_pecha_id, pecha_path):
    meta_path = Path(f"{pecha_path}/{new_pecha_id}.opf/meta.yml")
    meta = load_yaml(meta_path)
    meta['id'] = new_pecha_id
    dump_yaml(meta, meta_path)


def rename_opf_dir_name(new_pecha_id, pecha_path):
    pecha_id = pecha_path.stem
    subprocess.run(f'cd {pecha_path}; git mv {pecha_id}.opf {new_pecha_id}.opf', shell=True)

    
def update_repo_name(pecha_path, token):
    meta = load_yaml(Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml"))
    new_pecha_id = meta['id']
    rename_opf_dir_name(new_pecha_id, pecha_path)
    rename_meta(new_pecha_id, pecha_path)
    update_readme(new_pecha_id, pecha_path)
    rename_repo(new_pecha_id, pecha_path, token)
    return new_pecha_id
