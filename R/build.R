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
#' @export
build <- function(
  dockerfile = here::here("Dockerfile"),
  image_name = "tugboat",
  tag = "latest",
  platforms = c("linux/amd64", "linux/arm64"),
  build_args = NULL,
  build_context = dirname(dockerfile),
  push = FALSE,
  dh_username = NULL,
  dh_password = NULL
) {
  if (push) {
    if (is.null(dh_username) || is.null(dh_password)) {
      stop("Both `dh_username` and `dh_password` must be provided")
    }
    system(
      sprintf(
        "echo '%s' | docker login -u %s --password-stdin",
        dh_password,
        dh_username
      ),
      intern = FALSE,
      ignore.stderr = FALSE,
      receive.console.signals = TRUE
    )
  }
  if (is.null(dh_username)) {
    repository <- image_name
  } else {
    repository <- paste0(dh_username, "/", image_name)
  }
  exec_args <- c(
    "buildx",
    "build",
    "-f",
    dockerfile,
    "--platform",
    paste0(platforms, collapse = ","),
    "-t",
    paste0(repository, ":", tag),
    build_args,
    build_context,
    if (push) "--push" else NULL
  )
  system2(
    "docker",
    exec_args,
    receive.console.signals = TRUE
  )
  return(paste0(repository, ":", tag))
}
