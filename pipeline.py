import os
import json
import shutil
import logging
from git import Repo
from pathlib import Path
from github import Github
from urllib.request import urlopen
from rename_repo_name import update_repo_name
from update_pecha_base_and_meta import update_base_and_layer_name, update_meta


url = "https://raw.githubusercontent.com/OpenPecha-dev/editable-text/main/t_text_list.json"
response = urlopen(url)
t_text_list_dictionary = json.loads(response.read())


logging.basicConfig(
    filename="pecha_id_changed.log",
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


def update_pedurma_pechas(parser, token):
    commit_msg = "updated base name and meta.yml"
    output_path = Path(f"./pedurma_pechas/")
    for text_id, info in t_text_list_dictionary.items():
        if text_id == "D1115":
            google_id = info['google']
            namsel_id = info['namsel']
            google_path = download_pecha(google_id, output_path)
            namsel_path = download_pecha(namsel_id, output_path)
            google_base_dic = update_base_and_layer_name(google_path)
            update_meta(google_path, google_base_dic, parser, token)
            namsel_base_dic = update_base_and_layer_name(namsel_path)
            update_meta(namsel_path, namsel_base_dic, parser, token)
            if len(google_id) > 9:
                new_google_id = update_repo_name(google_path, token)
                notifier(f"{google_id} is {new_google_id}")
                repo_name_changed = True
            if len(namsel_id) > 9:
                new_namsel_id = update_repo_name(namsel_path, token)
                notifier(f"{namsel_id} is {new_namsel_id}")
                repo_name_changed = True
            if repo_name_changed == True:
                commit_msg = "updated base name, meta.yml and changed repo_name"
                push_changes(namsel_path, commit_msg, token)
                push_changes(google_path, commit_msg, token)
                clean_dir(google_path)
                clean_dir(namsel_path)
                delete_repo_from_github(google_path, new_google_id, token)
                delete_repo_from_github(namsel_path, new_namsel_id, token)
            else:
                push_changes(namsel_path, commit_msg, token)
                push_changes(google_path, commit_msg, token)
                clean_dir(google_path)
                clean_dir(namsel_path)


def update_google_ocr_pechas(parser, token):
    pecha_ids = ["P004437"]
    output_path = f"./google_ocr_pechas"
    commit_msg = "corrected meta"
    for pecha_id in pecha_ids:
        pecha_path = download_pecha(pecha_id, output_path)
        base_dic = update_base_and_layer_name(pecha_path)
        base_dic = None
        update_meta(pecha_path, base_dic, parser, token)
        push_changes(pecha_path, commit_msg, token)
        clean_dir(pecha_path)


if __name__ == "__main__":
    token = os.environ['GITHUB_TOKEN']
    pedurma_parser = "https://github.com/OpenPecha-dev/openpecha-toolkit/blob/a7eec5e12ddce18d0ed1dbb732a42cf48f94dd09/openpecha/formatters/hfml.py"
    google_ocr_parser = "https://github.com/OpenPecha-dev/openpecha-toolkit/blob/231bba39dd1ba393320de82d4d08a604aabe80fc/openpecha/formatters/google_orc.py"
    update_pedurma_pechas(pedurma_parser, token)
    update_google_ocr_pechas(google_ocr_parser, token)