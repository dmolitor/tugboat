lockfile <- renv::snapshot(project = NULL, type = "implicit")

#' Create an renv lockfile
#' 
#' This function is nearly identical to [renv::snapshot], with a couple
#' tiny tweaks. All arguments are passed directly to [renv::snapshot],
#' so the functionality is identical.
#' 
#' @param project The project directory. If NULL, then the active project
#'   will be used. If no project is currently active, then the current working
#'   directory is used instead.
#' @param lockfile The location where the generated lockfile should be written.
#'   By default, the lockfile is written to a file called renv.lock in the
#'   project directory. When NULL, the lockfile (as an R object) is returned
#'   directly instead.
#' @param ... All additional arguments are passed directly to [renv::snapshot].
#'   Please see the documentation for that function for all relevant details.
#'
#' @return A string giving the location of the generated lockfile.
#' @seealso [renv::snapshot] which this function relies on.
#' @examples
#' \dontrun{
#' init_renv()
#' }
#' @export
init_renv <- function(
  project = NULL,
  lockfile = renv::paths$lockfile(project = project),
  ...
) {
  snap <- renv::snapshot(project = project, lockfile = lockfile, ...)
  return(lockfile)
}


#' Create a Dockerfile
#' 
#' This function will crawl all files in the current project/directory and
#' (attempt to) detect all R packages and store these in a lockfile. From this
#' lockfile, it will create a corresponding Dockerfile.
#' 
#' @path project The project directory. If no project directory is provided, 
#'   by default, the [here] package will be used to determine the active
#'   project. If no project is currently active, then [here] defaults to
#'   the working directory where initially called.
#' @param project_args A list of all additional arguments which are passed
#'   directly to [renv::snapshot]. Please see the documentation for that
#'   function for all relevant details.
#' @param as The file path to write to. If NULL (the default), the Dockerfile
#'   will not be written.
#' @param ... Additional arguments for creating the Dockerfile that are passed
#'   directly to [dockerfiler::dock_from_renv]. Please see the documentation
#'   for that function for all relevant details.
#' 
#' @return A [dockerfiler::Dockerfile] object. You can then use this to do any
#'   further actions supported by the [dockerfiler] package.
#' @seealso [here::here]; this will be used by default to determine the current
#'   project directory.
#' @seealso [renv::snapshot] which this function relies on to find all R
#'   dependencies and create a corresponding lockfile.
#' @examples
#' \dontrun{
#' # Create a Dockerfile based on the rocker/rstudio image
#' dock <- create(project = here::here(), FROM = "rocker/rstudio")
#' # Write the Dockerfile locally
#' dock$write(as = here::here("Dockerfile"))
#' # Run the image locally with RStudio mounted on port 8787
#' 
#' }
#' @export
create <- function(
  project = here::here(),
  project_args = NULL,
  as = NULL,
  ...
) {
  lockfile <- do.call(init_renv, c(list(project = project), project_args))
  dockerfiler_args <- list(...)
  if ("use_pak" %in% names(dockerfiler_args)) {
    use_pak <- dockerfiler_args$use_pak
    dockerfiler_args$use_pak <- NULL
  } else {
    use_pak <- TRUE
  }
  dock <- dockerfiler::dock_from_renv(
    lockfile = lockfile,
    use_pak =  use_pak,
    ...
  )
  if (!is.null(as)) dock$write(as = as)
  return(dock)
}
