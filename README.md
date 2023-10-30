# tugboat

A tool for quickly generating a Docker image from a directory and allowing
the user to interact with that Docker image.

## Installation

As tugboat is still very early on in it's development, it can be installed from
TestPyPi with the following:
```python
python3 -m pip install --index-url https://test.pypi.org/simple/ tugboat
```

## Usage

Now, the tugboat cli should be available to use. To get a quick overview, use
the `info` command:
```
tugboat info
#| ℹ️  Execute `tugboat build` to build a Docker image from a local directory.
#| ℹ️  Execute `tugboat run` to run an existing image created from a directory.
#| ℹ️  Add the `--dryrun` argument to test either `build` or `run` without actually running anything.
#| ℹ️  Execute `tugboat --help` for more details.
```

### Turn your directory into a Docker image

The goal is for this to be as simple for the user as possible. Simply run
```
tugboat build
```
and it will walk you through all the steps.

If you want to get a feel for the user experience without actually building
anything (which can be quite time consuming), run
```
tugboat build --dryrun
```
This will walk you through the entire process without creating anything, so you
can get a feel for the process.
