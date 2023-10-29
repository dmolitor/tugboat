from build import ImageBuilder
import click
from config import TugboatConfig
from construct import DockerfileGenerator
from run import ResourceManager
from utils import check_docker

def execute(dryrun):
    docker_installed = check_docker()
    if not docker_installed:
        return False
    config = TugboatConfig()
    config.generate_config()
    dockerfile = DockerfileGenerator(config=config)
    dockerfile.dockerfile_create()
    imgbuilder = ImageBuilder(generator=dockerfile)
    imgbuilder.image_build(dryrun=dryrun)
    rmanager = ResourceManager(image_builder=imgbuilder)
    rmanager.run()
    return rmanager

@click.group()
@click.option("--dryrun", is_flag=True, default=False, help="Test a Tugboat command without actually running anything.")
@click.pass_context
def cli(ctx, dryrun):
    ctx.obj["DRYRUN"] = dryrun

@cli.command(help="Build a Docker image from the working directory.")
@click.option("--dryrun", is_flag=True, default=False)
@click.pass_context
def build(ctx, dryrun):
    try:
        if dryrun:
            ctx.obj["DRYRUN"] = True
        repo = execute(ctx.obj["DRYRUN"])
        if not repo:
            return False
    finally:
        if repo:
            repo._rstudio_kill()
            repo._jupyter_kill()

@cli.command(help="Run an existing Tugboat Docker image.")
@click.option("--dryrun", is_flag=True, default=False)
@click.pass_context
def run(ctx, dryrun):
    try:
        if dryrun:
            ctx.obj["DRYRUN"] = True
        repo = execute(ctx.obj["DRYRUN"])
        if not repo:
            return False
    finally:
        if repo:
            repo._rstudio_kill()
            repo._jupyter_kill()

@cli.command(help="Print a user-friendly guide to Tugboat.")
@click.pass_context
def info(ctx):
    print(
        "ℹ️  Execute `tugboat build` to build a Docker image from a local directory."
        + "\nℹ️  Execute `tugboat run` to run an existing image created from a directory."
        + "\nℹ️  Add the `--dryrun` argument to test either `build`"
        + " or `run` without actually running anything."
        + "\nℹ️  Execute `tugboat --help` for more details."
    )

if __name__ == "__main__":
    cli(obj={})