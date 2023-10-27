import click
from gangway import ui

@click.command()
@click.option("--build", is_flag=True, help="Build Docker image from local directory.")
@click.option("--run", is_flag=True, help="Interactively work with Docker image")
def execute(build, run):
    if run:
        build = True
    if build or run:
        docker_installed = ui.check_docker()
        if docker_installed == -1:
            return False
        repo = ui.load_config()
        if repo == -1:
            return False
        try:
            repo = ui.find_local_build(repo)
            repo = ui.orchestrate_build(repo)
            if repo == -1:
                return False
            repo = ui.launch_container(repo)
            if repo == -1:
                return False
        finally:
            repo.rstudio_kill()
            repo.jupyter_kill()
    else:
        print(
            "[x] Execute `gangway --build` to build a Docker image from the local directory."
            + "\n[x] Execute `gangway --run` to run a pre-existing Docker image in the local directory."
            + "\n[x] Execute `gangway --help` for more details."
        )
        return True

if __name__ == "__main__":
    execute()
