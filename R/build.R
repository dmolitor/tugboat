is_windows_rstudio <- function() {
  is_rstudio <- Sys.getenv("RSTUDIO") == "1"
  is_windows <- .Platform$OS.type == "windows"
  return(is_rstudio && is_windows)
}

build_image <- function(
    dockerfile,
    platforms,
    repository,
    tag,
    build_args,
    build_context,
    push,
    verbose
) {
  if (is_windows_rstudio()) {
    tmp <- tempfile()
    dir.create(tmp)
    on.exit({
      if (dir.exists(tmp)) unlink(tmp, recursive = TRUE, force = TRUE)
    }, add = TRUE)
    # Copy the build context over to a temp directory; our new build context!
    got_copied <- file.copy(
      list.files(
        build_context,
        full.names = TRUE,
        all.files = TRUE,
        no.. = TRUE
      ),
      tmp,
      recursive = TRUE
    )
    stopifnot(all(got_copied))
    # The temp directory is the new build context!
    build_context <- tmp
  }
  exec_args <- c(
    "buildx",
    "build",
    "-f",
    normalizePath(dockerfile, mustWork = FALSE),
    "--platform",
    paste0(platforms, collapse = ","),
    "-t",
    paste0(repository, ":", tag),
    build_args,
    build_context,
    if (push) "--push" else NULL
  )
  if (verbose) {
    msg <- paste0("Building:\n", paste0(c("docker", exec_args), collapse = " "))
    cat(msg, "\n")
  }
  build_status <- system2(
    "docker",
    exec_args
  )
  if (build_status != 0) {
    stop("Build failed with the following status: ", build_status)
  }
  return(TRUE)
}

#' Build a Docker image
#'
#' A simple utility to quickly build a Docker image from a Dockerfile.
#' 
#' @param dockerfile The path to the Dockerfile. The default value
#'   is a file named `Dockerfile` in the project directory surfaced by
#'   [here::here].
#' @param image_name A string specifying the Docker image name. Default
#'   is `tugboat`.
#' @param tag A string specifying the image tag. Default is `latest`.
#' @param platforms A vector of strings. Which platforms to build images for.
#'   Default is both `linux/amd64` and `linux/arm64`.
#' @param build_args A vector of strings specifying additional build arguments
#'   to pass to the `docker buildx build` command. Optional.
#' @param build_context The directory that is the build context for the
#'   image(s). Default value is the directory returned by [here::here].
#' @param push A boolean indicating whether to push to DockerHub.
#' @param dh_username A string specifying the DockerHub username. Only
#'   necessary if `push == TRUE`.
#' @param dh_password A string specifying the DockerHub password. Only
#'   necessary if `push == TRUE`.
#' @param verbose A boolean. Whether to print the actual Docker build
#'   command or not. Defaults to `FALSE`.
#' @returns The name of the built Docker image as a string.
#' @examples
#' \dontrun{
#' dock <- create(
#'   project = here::here(),
#'   FROM = "rstudio/r-base:devel-bookworm",
#'   exclude = c("/data", "/examples")
#' )
#' 
#' image_name <- build(
#'   dockerfile = here::here("Dockerfile"),
#'   image_name = "awesome_analysis",
#'   push = TRUE,
#'   dh_username = Sys.getenv("DH_USERNAME"),
#'   dh_password = Sys.getenv("DH_PASSWORD")
#' )
#' }
#' @export
build <- function(
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
) {
  stop_if_docker_not_installed()
  if (push) {
    if (is.null(dh_username) || is.null(dh_password)) {
      stop("Both `dh_username` and `dh_password` must be provided")
    }
    cat(system(
      sprintf(
        "echo '%s' | docker login -u %s --password-stdin",
        dh_password,
        dh_username
      ),
      intern = TRUE,
      ignore.stderr = FALSE
    ))
  }
  if (is.null(dh_username)) {
    repository <- image_name
  } else {
    repository <- paste0(dh_username, "/", image_name)
  }
  build_image(
    dockerfile = dockerfile,
    platforms = platforms,
    repository = repository,
    tag = tag,
    build_args = build_args,
    build_context = build_context,
    push = push,
    verbose = verbose
  )
  return(paste0(repository, ":", tag))
}
