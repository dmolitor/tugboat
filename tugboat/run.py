from tugboat.build import ImageBuilder
from tugboat.config import TugboatConfig
from tugboat.construct import DockerfileGenerator
import os
import prompt_toolkit as pt
import shutil
import subprocess
import tempfile
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tugboat.validators import number_validator, yes_no_validator
import webbrowser

class ResourceManager:
    """Manage Docker containers based on your built Docker image.
    
    ResourceManager will run containers and remove containers for the user.
    These containers will allow the user to interact with the resources in
    their image using IDEs including RStudio, Jupyter, etc.
    
    Parameters
    ----------
    image_builder : ImageBuilder
        An object of class `ImageBuilder`. This will include all settings
        from our built Docker image
    
    Attributes
    ----------
    
    Methods
    -------
    run()
        Allows the user to pick their method of choice to interact with the
        Docker image.
    """
    def __init__(self, image_builder):
        self._active_jupyter_session = False
        self._active_rstudio_session = False
        self._image_builder = image_builder
        self._jupyter_container = None
        self._jupyter_url = "http://localhost:8888/"
        self._jupyter_token = "tugboat"
        self._rstudio_container = None
        self._rstudio_url = "http://localhost:8787/"
        self._stata_lic = None
    
    def _get_stata_license(self):
        if self._stata_lic:
            return self._stata_lic
        Tk().withdraw()
        file_name = askopenfilename()
        print(f"File picked is: {file_name}")
        file_ext = file_name.split(".").pop()
        print(f"Is file extension okay: {file_ext}")
        if file_ext != "lic":
            yn = pt.prompt(
                (
                    "Typically a Stata license file ends with a .lic extension"
                    + f"\nThe file you provided is {filename}"
                    + "\nAre you sure this is the correct Stata license file?"
                    + " [Y/n] :"
                ),
                validator=yes_no_validator,
                validate_while_typing=True
            )
            if yn.lower() in ["n", "no"]:
                self._browse_stata_license()
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "stata.lic")
        print(f"Temp file name is: {temp_file}")
        file_name = shutil.copy2(file_name, temp_file)
        self._stata_lic = file_name
        return self._stata_lic
    
    def _jupyter_kill(self, force=True):
        if not self._active_jupyter_session:
            return True
        if force:
            cmd_args = ["docker", "remove", "-f", self._jupyter_container]
        else:
            cmd_args = ["docker", "remove", self._jupyter_container]
        container = subprocess.run(cmd_args, capture_output=True)
        container.check_returncode()
        self._jupyter_container = None
        self._active_jupyter_session = False
        return True

    def _jupyter_launch(self):
        if self._active_jupyter_session:
            tab_status = webbrowser.open_new_tab(
                self.jupyter_url + "lab?token=" + self.jupyter_token
            )
            return tab_status
        jupyter_container = "docker_jupyter"
        args = self._launcher_args()
        addtl_args = [
            "-d", "--name", f"{jupyter_container}",
            "-p", "8888:8888", "-e", f"JUPYTER_TOKEN={self._jupyter_token}",
            (self._image_builder._repository + ":" + self._image_builder._image_tag),
            "/init_jupyter"
        ]
        for a in addtl_args:
            args.append(a)
        container = subprocess.run(args, capture_output=True)
        container.check_returncode()
        self._active_jupyter_session = True
        self._jupyter_container = jupyter_container
        time.sleep(2)
        tab_status = webbrowser.open_new_tab(
            self._jupyter_url + "lab?token=" + self._jupyter_token
        )
        return tab_status
    
    def _launcher_args(self):
        launch_args = ["docker", "run"]
        if self._software_in_container("Stata"):
            print("It looks like you want to use Stata in your Docker image!")
            print("We will open a file browser. Please select your Stata license file ...")
            time.sleep(3)
            launch_args.append("--platform")
            launch_args.append("linux/amd64")
            stata_lic = self._get_stata_license()
            launch_args.append("-v")
            launch_args.append(f"{stata_lic}:/usr/local/stata/stata.lic")
        return launch_args
    
    def _rstudio_kill(self, force=True):
        if not self._active_rstudio_session:
            return True
        if force:
            cmd_args = ["docker", "remove", "-f", self._rstudio_container]
        else:
            cmd_args = ["docker", "remove", self._rstudio_container]
        container = subprocess.run(cmd_args, capture_output=True)
        container.check_returncode()
        self._rstudio_container = None
        self._active_rstudio_session = False
        return True

    def _rstudio_launch(self):
        if self._active_rstudio_session:
            tab_status = webbrowser.open_new_tab(self._rstudio_url)
            return tab_status
        rstudio_container = "docker_rstudio"
        args = self._launcher_args()
        addtl_args = [
            "-d", "--name", f"{rstudio_container}",
            "-p", "8787:8787", "-e", "ROOT=true", "-e",
            "DISABLE_AUTH=true",
            (self._image_builder._repository + ":" + self._image_builder._image_tag),
            "/init"
        ]
        for a in addtl_args:
            args.append(a)
        container = subprocess.run(args, capture_output=True)
        container.check_returncode()
        self._active_rstudio_session = True
        self._rstudio_container = rstudio_container
        time.sleep(2)
        tab_status = webbrowser.open_new_tab(self._rstudio_url)
        return tab_status
    
    def _software_in_container(self, software: str):
        is_in = software in self._image_builder._generator.requirements
        return is_in
    
    def run(self):
        dryrun = self._image_builder._dryrun
        check = True
        while check:
            print("How you would like to interact with the analysis:")
            print("1. RStudio")
            print("2. Jupyter")
            print("3. Quit")
            choice = pt.prompt(
                "Enter your choice (1/2/3): ",
                validator=number_validator,
                validate_while_typing=True
            )
            if choice == "1" and not dryrun:
                rstudio_in_container = self._software_in_container("RStudio")
                if rstudio_in_container:
                    self._rstudio_launch()
                else:
                    print(
                        "🫢 Oops it looks like RStudio isn't installed. "
                        + "You may need to edit your config file!"
                    )
            elif choice == "2" and not dryrun:
                jupyter_in_container = self._software_in_container("Jupyter")
                if jupyter_in_container:
                    self._jupyter_launch()
                else:
                    print(
                        "🫢 Oops it looks like Jupyter isn't installed. "
                        + "You may need to edit your config file!"
                    )
            elif choice == "3":
                check = False
        return self

# if __name__ == "__main__":
#     test_config = TugboatConfig()
#     test_config.generate_config()
#     test_dockerfile = DockerfileGenerator(config=test_config)
#     test_dockerfile.dockerfile_create()
#     test_imgbuilder = ImageBuilder(generator=test_dockerfile)
#     test_imgbuilder.image_build(dryrun=True)
#     test_rmanager = ResourceManager(image_builder=test_imgbuilder)
#     test_rmanager.run()
#     print(test_imgbuilder)
