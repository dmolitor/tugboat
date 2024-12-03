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
#' @param project_args A list of all additional arguments which are passed
#'   directly to [renv::snapshot]. Please see the documentation for that
#'   function for all relevant details.
#' @param as The file path to write to. If NULL, the Dockerfile
#'   will not be written. The default value is
#'   `file.path(project, "Dockerfile")`.
#' @param ... Additional arguments for creating the Dockerfile that are passed
#'   directly to [dockerfiler::dock_from_renv]. Please see the documentation
#'   for that function for all relevant details.
#' @param exclude A vector of strings specifying all paths (files or
#'   directories) that should NOT be included in the Docker image. By default,
#'   all files in the directory will be included. NOTE: the file and directory
#'   paths should be relative to the project directory. They do NOT need to
#'   be absolute paths.
#' 
#' @returns A [dockerfiler::Dockerfile] object. You can then use this to do any
#'   further actions supported by the dockerfiler package.
#' @seealso [here::here]; this will be used by default to determine the current
#'   project directory.
#' @seealso [renv::snapshot] which this function relies on to find all R
#'   dependencies and create a corresponding lockfile.
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
#' @export
create <- function(
  project = here::here(),
  project_args = NULL,
  as = file.path(project, "Dockerfile"),
  ...,
  exclude = NULL
) {
  lockfile <- do.call(init_renv, c(list(project = project), project_args))
  dockerfiler_args <- list(...)
  if ("use_pak" %in% names(dockerfiler_args)) {
    use_pak <- dockerfiler_args$use_pak
    dockerfiler_args$use_pak <- NULL
  } else {
    use_pak <- TRUE
  }
  dock <- do.call(
    dockerfiler::dock_from_renv,
    args = c(list(lockfile = lockfile, use_pak = use_pak), dockerfiler_args)
  )
  write_dockerignore(
    c(exclude, c("Dockerfile", ".dockerignore", "**/.DS_Store")),
    project = project
  )
  dock$COPY(".", paste0("/", basename(project)))
  if (!is.null(as)) dock$write(as = as)
  return(dock)
}

# Create an renv lockfile
# 
# This function is nearly identical to [renv::snapshot], with a couple
# tiny tweaks. All arguments are passed directly to [renv::snapshot],
# so the functionality is identical.
# 
# @param project The project directory. If NULL, then the active project
#   will be used. If no project is currently active, then the current working
#   directory is used instead.
# @param lockfile The location where the generated lockfile should be written.
#   By default, the lockfile is written to a file called renv.lock in the
#   project directory. When NULL, the lockfile (as an R object) is returned
#   directly instead.
# @param ... All additional arguments are passed directly to [renv::snapshot].
#   Please see the documentation for that function for all relevant details.
#
# @return A string giving the location of the generated lockfile.
# @seealso [renv::snapshot] which this function relies on.
# @examples
# \dontrun{
# init_renv()
# }
init_renv <- function(
  project = NULL,
  lockfile = renv::paths$lockfile(project = project),
  ...
) {
  snap <- renv::snapshot(project = project, lockfile = lockfile, ...)
  return(lockfile)
}

write_dockerignore <- function(exclude, project) {
  if (is.null(exclude)) return(TRUE)
  writeLines(exclude, file.path(project, ".dockerignore"))
  invisible(TRUE)
}