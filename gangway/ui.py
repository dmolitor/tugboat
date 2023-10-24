from gangway.convert import Repository
from datetime import datetime
import getpass
import json
import os
import shutil

def check_docker() -> int:
    exists = shutil.which("docker")
    if not exists:
        print(":( Docker is not installed. Visit https://docs.docker.com/get-docker/ to get started!")
        return -1
    else:
        print("[x] Docker is installed. We should be good to go!")
        return 1

def launch_container(repo):
    while True:
        print("How you would like to interact with the analysis:")
        print("1. RStudio")
        print("2. Jupyter")
        print("3. Quit")
        choice = input("Enter your choice (1/2/3): ")
        if choice == "1":
            repo.rstudio_launch()
        elif choice == "2":
            repo.jupyter_launch()
        elif choice == "3":
            return repo

def find_local_build(repo):
    try:
        repo.from_lockfile()
        return repo
    except Exception:
        return repo

def orchestrate_build(repo) -> int:
    if repo.built:
        with open(os.path.join(repo.dockerfile_dir, "gangway.lock"), "r") as g:
            lockfile = json.load(g)
        dt = str(datetime.strptime(
            lockfile["ImageInfo"]["Metadata"]["LastTagTime"].split(".")[0],
            "%Y-%m-%dT%H:%M:%S"
        ))
        print(
            "It looks like you've already built a Docker image with the following info:\n"
            + f"[x] Image Name: {repo.repository + ':' + repo.image_tag}\n"
            + f"[x] Timestamp: {dt}"
        )
        resp = input("Should we use this existing image? (Yes/No) [Y/n]: ")
        if resp.lower() in ["yes", "y"]:
            return repo

    resp = input("Continue converting your directory into a Docker container? (Yes/No) [Y/n]: ")
    if resp.lower() in ["no", "n"]:
        return -1

    print("Next, you will need to provide your Docker Hub username and password.\nIf you don't have an account, please create one here: https://hub.docker.com/signup")
    username = input("Username: ")
    pwd = getpass.getpass("Password: ")
    image_name = input("What do you want to name it? (e.g. docker-analysis): ")
    if not image_name:
        image_name = "gangway"
    tag = input("Is there a special tag you want to use? (e.g. 1.0) If not, hit enter and we will use 'latest' by default: ")
    if not tag:
        tag = "latest"

    repo = Repository("./gangway.yml")
    repo.create_dockerfile().write_dockerfile().build(username, pwd, image_name, tag)
    print("Done building the Docker image!")
    print("Uploading image to Docker Hub...")
    repo.dockerhub_push(username, pwd)
    print("Finished!")
    return repo

def load_config():
    config_exists = os.path.isfile("./gangway.yml")
    if not config_exists:
        out = f"{os.path.join(os.path.abspath('.'), 'gangway.yml')} does not exist"
        print(out)
        return -1
    repo = Repository("./gangway.yml")
    print("Based on your configuration file your software requirements are:")
    for s in repo.requires:
        print(f"[x] {s.capitalize()}: {repo._software_version(s, 'latest')}")
    resp = input("Is this list correct? (Yes/No) [Y/n]: ")
    if resp.lower() in ["no", "n"]:
        print(":( That's too bad. I can't help with that right now...Goodbye!")
        return -1
    return repo

def stop_on_error(val):
    if val == -1:
        raise Exception("Exiting process... Goodbye!")
    return val
