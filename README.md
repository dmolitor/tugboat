# tugboat

A tool for quickly generating a Docker image from a directory and allowing
the user to interact with that Docker image.

## Building

First, install all dependencies:
```
pip install -r requirements.txt
```

Next, build the package
```
python -m build
```

Then, you should be able to pip install locally using the buil .whl file:
```
pip install dist/tugboat-0.0.2-py3-none-any.whl
```

## Usage

Now, the gangway cli should be available to use:
```
gangway
#| [x] Execute `tugboat --build` to build a Docker image from the local directory.
#| [x] Execute `tugboat --run` to run a pre-existing Docker image in the local directory.
#| [x] Execute `tugboat --help` for more details.
```

## Build a Docker image

You need a .yaml file basically specifying if you need R and Python. Can be as
simple as:
```yaml
R:
  version: 4.3.1
Python:
  version: 3.11
```
Save this as `tugboat.yml` in the root directory.

Then simply run tugboat and it will walk you through all the steps.
```
tugboat --build
```
