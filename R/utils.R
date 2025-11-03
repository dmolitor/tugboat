# Search the project directory (and children) for DESCRIPTION files
description_files <- function(project) {
  files <- list.files(
    project,
    pattern = "^DESCRIPTION$",
    recursive = TRUE,
    full.names = TRUE
  )
  if (length(files) == 0) {
    return(NULL)
  }
  return(files)
}

# Extract the package name from a DESCRIPTION file
extract_package_name <- function(path) {
  description <- read.dcf(path)
  if ("Package" %in% colnames(description)) {
    return(unname(description[1, "Package", drop = TRUE]))
  } else {
    return(NULL)
  }
}

# Extract package names from a vector of DESCRIPTION files
extract_package_names <- function(project) {
  descriptions <- description_files(project)
  package_names <- unlist(lapply(descriptions, extract_package_name))
  return(unique(package_names))
}

# Initialize the renv lockfile from the project directory
init_renv <- function(
  project,
  lockfile = renv::paths$lockfile(project = project),
  ...
) {
  if (!interactive()) {
    pkgs_to_exclude <- unique(c(
      basename(project),
      extract_package_names(project)
    ))
    renv::install(project = project, exclude = pkgs_to_exclude)
  }
  snap <- renv::snapshot(project = project, lockfile = lockfile, ...)
  return(lockfile)
}

stop_if_docker_not_installed <- function() {
  is_installed <- Sys.which("docker") != ""
  if (!is_installed) {
    stop(
      c(
        "Docker is not installed. ",
        "Visit https://docs.docker.com/get-docker/ to get started!"
      ),
      call. = parent.frame()
    )
  }
}

# Write the .dockerignore in the project directory
write_dockerignore <- function(exclude, project) {
  if (is.null(exclude)) return(TRUE)
  writeLines(exclude, file.path(project, ".dockerignore"))
  invisible(TRUE)
}