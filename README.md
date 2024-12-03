# tugboat

A simple R package to generate a Dockerfile and corresponding Docker image
from an analysis directory. tugboat uses the [renv](https://github.com/rstudio/renv) package to automatically
detect all the packages necessary to replicate your analysis and will generate
a Dockerfile that contains an exact copy of your entire directory with all
the packages installed.

tugboat builds directly on the [dockerfiler](https://github.com/ThinkR-open/dockerfiler)
package which generates Dockerfiles from DESCRIPTION files or from `renv.lock`
files. tugboat adds the sugar of converting an unstructured analysis folder
into the necessary `renv.lock` file and then relies on dockerfiler to do
the rest.

tugboat may be of use, for example, when preparing a replication package for
research. With tugboat, you can take a directory on your local computer
and quickly generate a Dockerfile and Docker image that contains all the
code and the necessary software to reproduce your findings.

## Installation

Install tugboat with
```r
# install.packages("pak")
pak::pkg_install("dmolitor/tugboat")
```

## Usage

tugboat only has two exported functions; one to create a Dockerfile from your
analysis directory, and one to build the corresponding Docker image.

### Create the Dockerfile

The primary function from tugboat is `create`. This function will turn your
analysis directory into a Dockerfile that includes all your code and essential
R packages. For the most common cases, there are a couple arguments in this
function that are of particular importance:

- `project`: This argument tells tugboat which directory is the one to generate
the Dockerfile from. You can set this value yourself, or you can just use
the default value. By default, tugboat uses the `here::here` function to
determine what directory is the project directory. To get a detailed understanding
of exactly how this works take a look at the [here package](https://github.com/r-lib/here)
but in general, this "just works"!
- `as`: This argument tells tugboat where to save the Dockerfile. In
general you don't need to set this and tugboat will just save the
Dockerfile in the `project` directory from above.
- `exclude`: A vector of files or directories that should ***NOT***
be included in the Docker image. This is particularly important when you have,
for example, large data directories that you plan to mount to a container
instead of including them in the Docker image.

Below I'll outline a couple examples.
```r
library(tugboat)

# The simplest scenario where your analysis directory is your current
# active project, you are fine with the default base "rocker/r-base"
# Docker image, and you want to include all files/directories:
create()

# Suppose your analysis directory is actually a sub-directory of your
# main project directory:
create(project = here::here("sub-directory"))

# Suppose that you specifically need a Docker base image that has RStudio
# installed so that you can interact with your analysis within a Docker 
# container. To do this, we will pass additional arguments directly to the
# `dockerfiler::dock_from_renv function.
create(FROM = "rocker/rstudio")

# Finally, suppose that we want to include all files except a couple
# particularly data-heavy sub-directories:
create(exclue = c("data/big_directory_1", "data/big_directory_2"))
```

### Build the Docker image

Once the Dockerfile has been created, we can build the Docker image.
By default this will infer the Dockerfile directory using `here::here`.
This function assumes a little knowledge about Docker; if you aren't sure
where to start, [this is a great starting point](https://colinfay.me/docker-r-reproducibility/).

The following example will do the simplest thing and will build the
image locally.
```r
build(image_name = "awesome_analysis")
```

Suppose that, like above, your analysis directory is a sub-directory of
your main project directory:
```r
build(
  dockerfile = here::here("sub-directory"),
  image_name = "awesome_analysis"
)
```

### Push to DockerHub

If, instead of just building the Docker image locally, you want to build
the image and then push to DockerHub, you can make a couple small additions
to the code above:
```r
build(
  image_name = "awesome_analysis",
  push = TRUE,
  dh_username = Sys.getenv("DH_USERNAME"),
  dh_password = Sys.getenv("DH_PASSWORD")
)
```

Note: If you choose to push, you also need to provide your DockerHub
username and password. Typically you don't want to pass these in
directly and should instead use environment variables (or a similar
method) instead.

### Examples

For some worked examples of how to use tugboat in practice, see the
`examples/` directory.
