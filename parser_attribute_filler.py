import csv
import os
import yaml
from github import Github
from pathlib import Path


def update_repo(g, pecha_id, file_path, commit_msg, new_content):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"{file_path}", ref="master")
        repo.update_file(contents.path, commit_msg , new_content, contents.sha, branch="master")
        print(f'{pecha_id} update completed..')
    except:
        print(f"{pecha_id} repo not found")

def get_meta_from_opf(g, pecha_id):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
        return contents.decoded_content.decode()
    except:
        print('Repo Not Found')
        return ''

def get_new_meta(meta_data, parser_url):
    meta_data = yaml.safe_load(meta_data)
    meta_data['parser'] = parser_url
    meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
    return meta_yml

def fill_parser_url(pecha_id, parser_url):
    token = os.getenv('GITHUB_TOKEN')
    g = Github(token)
    commit_msg = 'meta updated'
    file_path = f"./{pecha_id}.opf/meta.yml"
    old_meta_data = get_meta_from_opf(g, pecha_id)
    new_meta_data = get_new_meta(old_meta_data, parser_url)
    update_repo(g, pecha_id, file_path, commit_msg, new_meta_data)
    print(f'INFO: {pecha_id} meta updated..')



if __name__ == "__main__":
    pecha_id = "PC4CFCFEB"
    parser_url = "https://github.com/OpenPecha-dev/openpecha-toolkit/blob/a7eec5e12ddce18d0ed1dbb732a42cf48f94dd09/openpecha/formatters/hfml.py"
    fill_parser_url(pecha_id, parser_url)
