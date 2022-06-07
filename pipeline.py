import time
import json
import shutil
import logging
from git import Repo
from pathlib import Path
from github import Github
from urllib.request import urlopen
from rename_repo_name import update_repo_name
from update_index import update_index_base
from openpecha.utils import load_yaml
from update_pecha_base_and_meta import update_base_and_layer_name, update_meta


url = "https://raw.githubusercontent.com/OpenPecha-dev/editable-text/main/t_text_list.json"
response = urlopen(url)
t_text_list_dictionary = json.loads(response.read())


logging.basicConfig(
    filename="ocr_pecha_id_changed.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)


config = {
    "OP_ORG": "https://github.com/Openpecha"
}


def clean_dir(layers_output_dir):
    if layers_output_dir.is_dir():
            shutil.rmtree(str(layers_output_dir))


def notifier(msg):
    logging.info(msg)


def check_new_pecha(pecha_id, g):
    repo = g.get_repo(f"Openpecha/{pecha_id}")
    contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
    if contents != None:
        return True
    else:
        return False
    
    
def _get_openpecha_org(org_name, token):
    """OpenPecha github org singleton."""
    g = Github(token)
    org = g.get_organization(org_name)
    return org

    
def delete_repo_from_github(pecha_path, new_pecha_id, token):
    pecha_id = pecha_path.name
    g = Github(token)
    check = check_new_pecha(new_pecha_id, g)
    if check == True:
        org = _get_openpecha_org("Openpecha", token)
        repo = org.get_repo(pecha_id)
        repo.delete()
        notifier(f"{pecha_id} is deleted from github")


def commit(repo, message, not_includes=[], branch="master"):
    has_changed = False

    for fn in repo.untracked_files:
        ignored = False
        for not_include_fn in not_includes:
            if not_include_fn in fn:
                ignored = True
        if ignored:
            continue
        if fn:
            repo.git.add(fn)
        if has_changed is False:
            has_changed = True

    if repo.is_dirty() is True:
        for fn in repo.git.diff(None, name_only=True).split("\n"):
            if fn:
                repo.git.add(fn)
            if has_changed is False:
                has_changed = True
        if has_changed is True:
            if not message:
                message = "Initial commit"
            repo.git.commit("-m", message)
            repo.git.push("origin", branch)        
    
        
def setup_auth(repo, org, token):
    remote_url = repo.remote().url
    old_url = remote_url.split("//")
    authed_remote_url = f"{old_url[0]}//{org}:{token}@{old_url[1]}"
    repo.remote().set_url(authed_remote_url)


def push_changes(pecha_path, commit_msg, token):
    repo = Repo(pecha_path)
    setup_auth(repo, "Openpecha", token)
    commit(repo, commit_msg, not_includes=[],branch="master")


def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "master"


def download_pecha(pecha_id, out_path=None, branch="master"):
    pecha_url = f"{config['OP_ORG']}/{pecha_id}.git"
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    pecha_path = out_path / pecha_id
    Repo.clone_from(pecha_url, str(pecha_path))
    repo = Repo(str(pecha_path))
    branch_to_pull = get_branch(repo, branch)
    repo.git.checkout(branch_to_pull)
    print(f"{pecha_id} Downloaded ")
    return pecha_path  

def reformat_opf(pecha_path, parser, token):
    pecha_base_dic = update_base_and_layer_name(pecha_path)
    update_meta(pecha_path, pecha_base_dic, parser, token)
    new_pecha_id = update_repo_name(pecha_path, token)
    return new_pecha_id


def update_pedurma_pechas(token):
    text_list = {}
    parser = ""
    commit_msg = "updated base name and meta.yml"
    commit_msg = "pecha refomated"
    text_list = ["D1109", "D1115"]
    output_path = Path(f"./pedurma_pechas/")
    for text_id, info in t_text_list_dictionary.items():
        if text_id in text_list:
            google_id = info['google']
            namsel_id = info['namsel']
            google_path = download_pecha(google_id, output_path)
            namsel_path = download_pecha(namsel_id, output_path)
            new_google_id = reformat_opf(google_path, parser, token)
            new_namsel_id = reformat_opf(namsel_path, parser, token)
            push_changes(namsel_path, commit_msg, token)
            notifier(f"{namsel_id} is {new_namsel_id}")
            time.sleep(30) 
            push_changes(google_path, commit_msg, token)
            notifier(f"{google_id} is {new_google_id}")
            time.sleep(30)
            notifier(f"{text_id} is done")
            clean_dir(google_path)
            clean_dir(namsel_path)
    
            
def check_initial_creation_type(pecha_path):
    meta = load_yaml(Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml"))
    if meta['initial_creation_type'] == "ocr":
        return True
    else:
        return False
    
    
def update_ocr_pechas(batch_num, parser, token):
    pecha_ids = (Path(f"./ocr-batches/{batch_num}.txt").read_text(encoding='utf-8')).splitlines()
    output_path = "./pechas"
    commit_msg = "updated to the new formate"
    for pecha_id in pecha_ids:
        pecha_path = download_pecha(pecha_id, output_path)
        check = check_initial_creation_type(pecha_path)
        if check == True:
            new_pecha_id = reformat_opf(pecha_path, parser, token)
            push_changes(pecha_path, commit_msg, token)
            notifier(f"{pecha_id} is {new_pecha_id}")
        
if __name__ == "__main__":
    batch_num = "Batch-1"
    token = "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"
    google_ocr_parser = "https://github.com/OpenPecha-dev/openpecha-toolkit/blob/231bba39dd1ba393320de82d4d08a604aabe80fc/openpecha/formatters/google_orc.py"
    update_ocr_pechas(batch_num, google_ocr_parser, token)