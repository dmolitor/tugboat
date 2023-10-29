# from build import ImageBuilder
# from config import TugboatConfig
# from construct import DockerfileGenerator
import prompt_toolkit as pt
import subprocess
from tugboat.validators import number_validator
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
        container = subprocess.run(
            [
                "docker", "run", "-d", "--name", f"{jupyter_container}",
                "-p", "8888:8888", "-e", f"JUPYTER_TOKEN={self._jupyter_token}",
                (self._image_builder.repository + ":" + self._image_builder.image_tag),
                "/init_jupyter"
            ],
            capture_output=True
        )
        container.check_returncode()
        self._active_jupyter_session = True
        self._jupyter_container = jupyter_container
        time.sleep(2)
        tab_status = webbrowser.open_new_tab(
            self._jupyter_url + "lab?token=" + self._jupyter_token
        )
        return tab_status

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
        container = subprocess.run(
            [
                "docker", "run", "-d", "--name", f"{rstudio_container}",
                "-p", "8787:8787", "-e", "ROOT=true", "-e",
                "DISABLE_AUTH=true",
                (self._image_builder.repository + ":" + self._image_builder.image_tag),
                "/init"
            ],
            capture_output=True
        )
        container.check_returncode()
        self._active_rstudio_session = True
        self._rstudio_container = rstudio_container
        time.sleep(2)
        tab_status = webbrowser.open_new_tab(self._rstudio_url)
        return tab_status
    
    def run(self):
        dryrun = self._image_builder._dryrun
        while True:
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
                self._rstudio_launch()
            elif choice == "2" and not dryrun:
                self._jupyter_launch()
            elif choice == "3":
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
