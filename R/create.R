#' Create a Dockerfile
#' 
#' This function will crawl all files in the current project/directory and
#' (attempt to) detect all R packages and store these in a lockfile. From this
#' lockfile, it will create a corresponding Dockerfile. It will also copy
#' the full contents of the current directory/project into the Docker image.
#' The directory in the Docker container containing the current directory
#' contents will be /current-directory-name. For example if your analysis
#' directory is named `incredible_analysis`, the corresponding location in
#' the generated Docker image will be `/incredible_analysis`.
#' 
#' @param project The project directory. If no project directory is provided, 
#'   by default, the here package will be used to determine the active
#'   project. If no project is currently active, then here defaults to
#'   the working directory where initially called.
#' @param as The file path to write to. The default value is
#'   `file.path(project, "Dockerfile")`.
#' @param FROM Docker image to start FROM. Default is FROM r-base:R.version.
#' @param ... Additional arguments which are passed directly to
#'   [renv::snapshot]. Please see the documentation for that function for all
#'   relevant details.
#' @param exclude A vector of strings specifying all paths (files or
#'   directories) that should NOT be included in the Docker image. By default,
#'   all files in the directory will be included. NOTE: the file and directory
#'   paths should be relative to the project directory. They do NOT need to
#'   be absolute paths.
#' 
#' @seealso [here::here]; this will be used by default to determine the current
#'   project directory.
#' @seealso [renv::snapshot] which this function relies on to find all R
#'   dependencies and create a corresponding lockfile.
#' @returns The Dockerfile contained as a string vector. Each vector element
#'   corresponds to a line in the Dockerfile.
#' @examples
#' \dontrun{
#' # Create a Dockerfile based on the rocker/rstudio image.
#' # Write the Dockerfile locally to here::here("Dockerfile").
#' # Copy all files except the /data and /examples directories.
#' dock <- create(
#'   project = here::here(),
#'   FROM = "rocker/rstudio",
#'   exclude = c("/data", "/examples")
#' )
#' }
#' 
#' @export
create <- function(
  project = here::here(),
  as = file.path(project, "Dockerfile"),
  FROM = NULL,
  ...,
  exclude = NULL
) {
  lockfile <- init_renv(project = project, ...)
  dock <- dockerfile(lockfile, FROM = FROM)
  dock <- c(dock, paste("COPY .", paste0("/", basename(project))), "")
  write_dockerignore(
    c(exclude, c("Dockerfile", ".dockerignore", "**/.DS_Store")),
    project = project
  )
  if (!is.null(as)) writeLines(dock, con = as)
  cat(dock, sep = "\n")
  invisible(dock)
}
