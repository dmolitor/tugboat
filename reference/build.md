# Build a Docker image

A simple utility to quickly build a Docker image from a Dockerfile.

## Usage

``` r
build(
  dockerfile = here::here("Dockerfile"),
  image_name = "tugboat",
  tag = "latest",
  platforms = c("linux/amd64", "linux/arm64"),
  build_args = NULL,
  build_context = here::here(),
  push = FALSE,
  dh_username = NULL,
  dh_password = NULL,
  verbose = FALSE
)
```

## Arguments

- dockerfile:

  The path to the Dockerfile. The default value is a file named
  `Dockerfile` in the project directory surfaced by
  [here::here](https://here.r-lib.org/reference/here.html).

- image_name:

  A string specifying the Docker image name. Default is `tugboat`.

- tag:

  A string specifying the image tag. Default is `latest`.

- platforms:

  A vector of strings. Which platforms to build images for. Default is
  both `linux/amd64` and `linux/arm64`.

- build_args:

  A vector of strings specifying additional build arguments to pass to
  the `docker buildx build` command. Optional.

- build_context:

  The directory that is the build context for the image(s). Default
  value is the directory returned by
  [here::here](https://here.r-lib.org/reference/here.html).

- push:

  A boolean indicating whether to push to DockerHub.

- dh_username:

  A string specifying the DockerHub username. Only necessary if
  `push == TRUE`.

- dh_password:

  A string specifying the DockerHub password. Only necessary if
  `push == TRUE`.

- verbose:

  A boolean. Whether to print the actual Docker build command or not.
  Defaults to `FALSE`.

## Value

The name of the built Docker image as a string.

## Examples

``` r
if (FALSE) { # \dontrun{
dock <- create(
  project = here::here(),
  FROM = "rstudio/r-base:devel-bookworm",
  exclude = c("/data", "/examples")
)

image_name <- build(
  dockerfile = here::here("Dockerfile"),
  image_name = "awesome_analysis",
  push = TRUE,
  dh_username = Sys.getenv("DH_USERNAME"),
  dh_password = Sys.getenv("DH_PASSWORD")
)
} # }
```
