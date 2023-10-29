import hashlib
import re
import shutil
import subprocess

def check_docker():
    exists = shutil.which("docker")
    if not exists:
        print("❌ Docker is not installed. Visit https://docs.docker.com/get-docker/ to get started!")
        return False
    else:
        print("✅ Docker is installed. We should be good to go!")
        return True

def hash_text(text: str):
    hash_object = hashlib.sha256(text.encode("utf-8"))
    return hash_object.hexdigest()

def image_info(digests=True):
    """Information on all local Docker images
    
    Executes and parses the result of `docker images`.
    
    Parameters
    ----------
    digests : bool, default=True
        Whether to pass the --digests flag to `docker images`.
    
    Returns
    -------
    dict
        Information regarding all local docker images stored as a dictionary.
    """
    if digests:
        args = ["docker", "images",  "--digests"]
    else:
        args = ["docker", "images"]
    image = subprocess.run(args, capture_output=True)
    image.check_returncode()
    image_info = [t.decode("UTF-8") for t in image.stdout.splitlines()]
    header = re.split(r"\s{2,}", image_info.pop(0))
    if len(image_info) == 0:
        return None
    image_info = [re.split(r"\s{2,}", t) for t in image_info]
    image_info = [{k:v for k, v in zip(header, i)} for i in image_info]
    return image_info

def keys_to_lower(d: dict):
    d = {key.lower(): d[key] for key in d.keys()}
    return d

def none_to_string(s):
    if s == None:
        return ""
    return s

def run(args, **kwargs):
    with subprocess.Popen(args, **kwargs) as process:
        if not process.stdout == None:
            for line in process.stdout:
                print(line.decode("utf8").rstrip("\n"))

def string_to_none(s):
    if s == "":
        return None
    return s
