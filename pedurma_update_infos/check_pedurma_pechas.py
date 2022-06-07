import logging
from pathlib import Path
from openpecha.utils import load_yaml
from github import Github


logging.basicConfig(
    filename="new_pecha_not_made.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)


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

    
def delete_repo_from_github(old_pecha_id, new_pecha_id, token):
    g = Github(token)
    check = check_new_pecha(new_pecha_id, g)
    if check == True:
        org = _get_openpecha_org("Openpecha", token)
        repo = org.get_repo(old_pecha_id)
        repo.delete()
        print(f"{old_pecha_id} is deleted")
    else:
        notifier(f"{old_pecha_id} is not made into new opf")
        
def check_pechas(ids, token):
    for old_pecha_id, new_pecha_id in ids.items():
        delete_repo_from_github(old_pecha_id, new_pecha_id, token)


if __name__ == "__main__":
    token = "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"
    ids = load_yaml(Path(f"./ids.yml"))
    check_pechas(ids, token)
    
    
    
    
    
    
    
    
