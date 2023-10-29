#from config import TugboatConfig
#from construct import DockerfileGenerator
from datetime import datetime
import getpass
import json
import prompt_toolkit as pt
import os
import subprocess
from tugboat.utils import hash_text, image_info, run, string_to_none
from tugboat.validators import yes_no_validator

class ImageBuilder:
    """Build a Docker image from a local directory.
    
    ImageBuilder will build a Dockerfile comprised of all files and dependencies
    contained within a local directory
    
    Parameters
    ----------
    generator : DockerfileGenerator
        An object of class `DockerfileGenerator`. This will include all relevant
        configuration settings for building our Docker image as well as
        the constructed Dockerfile.
    
    Attributes
    ----------
    config : dict
        Configuration settings structured as a dictionary.
    requirements : list of str
        A list of all software requirements.
    
    Methods
    -------
    """
    def __init__(self, generator):
        self._built = False
        self._dryrun = False
        self._image_name = None
        self._image_tag = None
        self._dh_username = None
        self._generator = generator
        self._repository = None
        self._repo_digest = None
        self._using_existing_dockerfile = generator._using_existing_dockerfile
        self._lockfile_exists = self._check_if_lockfile_exists()
    
    def _check_if_lockfile_exists(self):
        exists = os.path.isfile("tugboat.lock")
        return exists
    
    def _from_lockfile(self):
        if os.path.isfile("tugboat.lock"):
            with open("tugboat.lock", "r") as g:
                lockfile = json.load(g)
            self._repository = lockfile["Repository"]
            self._dh_username = lockfile["DHUsername"]
            self._image_name = lockfile["ImageName"]
            self._image_tag = lockfile["ImageTag"]
            self._repo_digest = lockfile["RepoDigest"]
            same_dockerfile_hash = (
              hash_text(self._generator._dockerfile) == lockfile["DockerfileHash"]
            )
            if same_dockerfile_hash:
                try:
                    dt = str(datetime.strptime(
                        lockfile["ImageInfo"]["Metadata"]["LastTagTime"].split(".")[0],
                        "%Y-%m-%dT%H:%M:%S"
                    ))
                except:
                    dt = None
                print(
                    "It looks like you've already built a Docker image with the following info:\n"
                    + f"✔ Image Name: {self._repository + ':' + self._image_tag}\n"
                    + f"✔ Timestamp: {string_to_none(dt)}"
                )
                yn = pt.prompt(
                    "Should we use this existing image? [Y/n]: ",
                    validator=yes_no_validator,
                    validate_while_typing=True
                )
                if yn.lower() in ["y", "yes"]:
                    self._built = True
                else:
                    self._built = False
            else:
                self._built = False
        else:
            self._built = False
        return self
    
    def _lockfile(self):
        repository = self._repository
        image_tag = self._image_tag
        if not self._dryrun:
            docker_inspect = subprocess.run(
                ["docker", "inspect", (repository + ":" + image_tag)],
                capture_output=True
            )
            docker_inspect.check_returncode()
            [docker_inspect] = json.loads(docker_inspect.stdout)
        else:
            docker_inspect = {}
        if not docker_inspect.get("RepoDigests") == None:
            self._repo_digest = docker_inspect["RepoDigests"]
        lockfile = {
            "Repository": self._repository,
            "ImageName": self._image_name,
            "ImageTag": self._image_tag,
            "DHUsername": self._dh_username,
            "RepoDigest": self._repo_digest,
            "ImageInfo": docker_inspect,
            "DockerfileHash": hash_text(self._generator._dockerfile)
        }
        lockfile_pretty = json.dumps(lockfile, indent=4)
        with open("tugboat.lock", "w+") as j:
            j.write(lockfile_pretty)
        return self
    
    def _prep_local_image(self, repository, tag):
        docker_inspect = subprocess.run(
            ["docker", "inspect", (repository + ":" + tag)],
            capture_output=True
        )
        if docker_inspect.returncode == 0:
            return True
        docker_pull = subprocess.run(
            ["docker", "pull", (repository + ":" + tag)],
            capture_output=True
        )
        if docker_pull.returncode > 0:
            return False
        return True
    
    def __repr__(self):
        status_str = (
            "Repository Status " + ("=" * 62)
            + "\n\nDocker Image:"
            + "\n✔ Dockerfile Directory: "
            + os.path.abspath(".")
            + "\n✔ Dockerfile Built: "
            + str(self.built)
            + f"\n✔ Image Name: {self._image_name}"
            + f"\n✔ Image Tag: {self._image_tag}"
            + f"\n✔ Username: {string_to_none(self._dh_username)}"
            + f"\n✔ Repository: {self._repository}"
            + f"\n✔ Repo Digest: {string_to_none(self._repo_digest)}"
            + f"\n✔ Using Existing Dockerfile: {self._using_existing_dockerfile}"
            + f"\n✔ Lockfile Exists: {self._lockfile_exists}"
        )
        return status_str
    
    def image_build(self, dryrun=False):
        if dryrun:
            self._dryrun = True
        print("Building Docker image ...")
        self._from_lockfile()
        if self._built:
            built = self._prep_local_image(self._repository, self._image_tag)
            if built:
                return self
            self._built = False
            print(
                "❌ Docker image in lockfile can't be found locally or retrieved" 
                + " from DockerHub\n🔄 Rebuilding image ..."
            )
        image_name = input("What do you want to name it? (e.g. docker-analysis): ")
        if not string_to_none(image_name):
            image_name = "tugboat"
        tag = input(
            "Is there a special tag you want to use (e.g. v1.0)?\n"
            + "If not, hit Enter/Return and we will use 'latest' by default: "
        )
        if not string_to_none(tag):
            tag = "latest"
        self._image_name = image_name
        self._image_tag = tag
        if not self._dh_username == None:
            self._repository = self._dh_username + "/" + image_name
        else:
            self._repository = image_name
        
        # Build the image
        if not dryrun:
            _ = run(
                ["docker", "build", "-t", (self._repository + ":" + self._image_tag), "."],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        self.built = True
        self._lockfile()
        
        # Push the image
        pt.print_formatted_text(
            pt.HTML(
                "Would you like to upload your new Docker image to DockerHub?\n❗<u>(This is "
                + "highly recommended so that your changes have a permanent record)</u>❗"
            )
        )
        upload = pt.prompt(
            "[Y/n]: ",
            validator=yes_no_validator,
            validate_while_typing=True
        )
        if upload.lower() in ["y", "yes"]:
            self.image_push()
        
        return self
    
    def image_push(self):
        # Get user credentials
        pt.print_formatted_text(pt.HTML(
           "ℹ️ To upload this image, you will need to provide your Docker Hub"
           + " username and password.\n   If you don't have an account, please"
           + " create one here: <u>https://hub.docker.com/signup</u>"
        ))
        username = input("Username: ")
        pwd = getpass.getpass("Password: ")
        
        # Login to DockerHub via cli
        login = subprocess.run(["echo", pwd, "|", "docker", "login", "-u", username, "--password-stdin"], capture_output=True)
        login.check_returncode()
        
        # If username has not been provided, we need to correctly tag the image
        image_id = username + "/" + self._image_name + ":" + self._image_tag
        if self._dh_username == None and not self._dryrun:
            docker_tag = subprocess.run(
                [
                    "docker", "tag", (self.repository + ":" + self.image_tag),
                    image_id
                ],
                capture_output=True
            )
            docker_tag.check_returncode()
        
        # Now push the Docker image
        if not self._dryrun:
            docker_push = run(["docker", "push", image_id])
        
        # Update attributes
        repo_str = username + "/" + self._image_name
        self._dh_username = username
        self._repository = repo_str
        
        # Update lockfile
        self._lockfile()
        return self

# if __name__ == "__main__":
#     test_config = TugboatConfig()
#     test_config.generate_config()
#     test_dockerfile = DockerfileGenerator(config=test_config)
#     test_dockerfile.dockerfile_create()
#     test_imgbuilder = ImageBuilder(generator=test_dockerfile)
#     test_imgbuilder.image_build(dryrun=True)
#     print(test_imgbuilder)
    
