# tugboat <img src='man/figures/logo-no-bg.png' align="right" height="140"/>

<!-- badges: start -->
[![R-CMD-check](https://github.com/dmolitor/tugboat/actions/workflows/R-CMD-check.yaml/badge.svg)](https://github.com/dmolitor/tugboat/actions/workflows/R-CMD-check.yaml)
[![pkgdown](https://github.com/dmolitor/tugboat/actions/workflows/pkgdown.yaml/badge.svg)](https://github.com/dmolitor/tugboat/actions/workflows/pkgdown.yaml)
[![CRAN status](https://www.r-pkg.org/badges/version/tugboat)](https://CRAN.R-project.org/package=tugboat)
<!-- badges: end -->

A simple R package to generate a Dockerfile and corresponding Docker image
from an analysis directory. tugboat uses the [renv](https://github.com/rstudio/renv/) package to automatically
detect all the packages necessary to replicate your analysis and will generate
a Dockerfile that contains an exact copy of your entire directory with all
the packages installed.

tugboat transforms an unstructured analysis folder into a renv.lock file
and constructs a Docker image that includes all your essential R packages
based on this lockfile.

tugboat may be of use, for example, when preparing a replication package for
research. With tugboat, you can take a directory on your local computer
and quickly generate a Dockerfile and Docker image that contains all the
code and the necessary software to reproduce your findings.

## Installation

Install tugboat from CRAN:
```r
install.packages("tugboat")
```

Or install the development version from GitHub:
```r
# install.packages("pak")
pak::pkg_install("dmolitor/tugboat")
```

## Usage

tugboat only has two exported functions; one to create a Dockerfile from your
analysis directory, and one to build the corresponding Docker image.

### Create the Dockerfile

The primary function from tugboat is `create()`. This function converts 
your analysis directory into a Dockerfile that includes all your code 
and essential R packages.

This function scans all files in the current analysis directory,
attempts to detect all R packages, and installs these packages in
the resulting Docker image. It also copies the entire contents of the
analysis directory into the Docker image. For example, if
your analysis directory is named `incredible_analysis`, the corresponding
location of your code and data files in the generated Docker image will
be `/incredible_analysis`.

For the most common use-cases, there are a couple of arguments in this
function that are particularly important:

- `project`: This argument tells tugboat which directory is the one to generate
the Dockerfile from. You can set this value yourself, or you can just use
the default value. By default, tugboat uses the `here::here` function to
determine what directory is the analysis directory. To get a detailed understanding
of exactly how this works take a look at the [here package](https://github.com/r-lib/here/).
In general, this "just works"!
- `as`: This argument tells tugboat where to save the Dockerfile. In
general you don't need to set this and tugboat will just save the
Dockerfile in the `project` directory from above.
- `exclude`: A vector of files or sub-directories in your analysis directory
that should ***NOT*** be included in the Docker image. This is particularly
important when you have, for example, a sub-directory with large data files
that would make the resulting Docker image extremely large if included. You
can tell tugboat to exclude this sub-directory and then simply mount it to
a Docker container as needed.

Below I'll outline a couple examples.
```r
library(tugboat)

# The simplest scenario where your analysis directory is your current
# active project, you are fine with the default base "r-base:latest"
# Docker image, and you want to include all files/directories:
create()

# Suppose your analysis directory is actually a sub-directory of your
# main project directory:
create(project = here::here("sub-directory"))

# Suppose that you specifically need a Docker base image that has RStudio
# installed so that you can interact with your analysis within a Docker 
# container. To do this, we will explicitly specify a different Docker
# base image using the `FROM` argument.
create(FROM = "rocker/rstudio")

# Finally, suppose that we want to include all files except a couple
# particularly data-heavy sub-directories:
create(exclude = c("data/big_directory_1", "data/big_directory_2"))
```

### Build the Docker image

Once the Dockerfile has been created, we can build the Docker image
with the `build()` function. By default this will infer the Dockerfile
directory using `here::here`. This function assumes a little knowledge
about Docker; if you aren't sure where to start,
[this is a great starting point](https://colinfay.me/docker-r-reproducibility/).

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

## Why tugboat? 🚢

There are a few available packages with similar goals, so why tugboat?
tugboat is minimal and builds directly on top of
[`renv`](https://rstudio.github.io/renv/articles/renv.html) and
[`pak`](https://pak.r-lib.org/).
Each of these packages is actively maintained and provides specific
utilities that the tugboat utilizes for maximum convenience.
tugboat aims to leverage packages that are likely to remain actively
maintained and handle dependency management as seamlessly as possible.

- [containerit](https://o2r.info/containerit/) is a robust package that is
directly comparable to tugboat. However, it implements its own method for
discovering R package dependencies instead of using renv. It also relies on
[sysreqsdb](https://github.com/r-hub/sysreqsdb) for system dependency
discovery, which has been archived in favor of
[r-system-requirements](https://github.com/rstudio/r-system-requirements),
which pak is built on. It also isn't super actively maintained and isn't on
CRAN.

- [holepunch](https://github.com/karthik/holepunch) is related but focuses
on making GitHub repositories Binder-compatible. It currently relies on MRAN,
which is now obsolete, and does not use pak for system dependency management.
It is also not actively maintained and is not on CRAN.

- [automagic](https://github.com/cole-brokamp/automagic) focuses on
automatically detecting and installing R package dependencies but uses its own
method rather than relying on renv. automagic also has no utilities for
creating/building Docker images.


## Examples

For some worked examples of how to use tugboat in practice, see the
`examples/` directory.
