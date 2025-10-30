check_if_installed <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE) && interactive()) {
    ans <- readline(paste0("Package '", pkg, "' is required. Install it now? [Y/n]: "))
    if (tolower(trimws(ans)) == "y" || ans == "") {
      renv::install(pkg)
    } else {
      stop(paste0("Package '", pkg, "' must be installed"))
    }
  } else if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(paste0("Package '", pkg, "' must be installed"))
  }
}

same_dir <- function(dir, path) {
  normalizePath(dir, winslash = "/", mustWork = FALSE) ==
    dirname(normalizePath(path, winslash = "/", mustWork = FALSE))
}

path_first_existing <- function(paths) {
  path_exists <- file.exists(paths)
  if (!any(path_exists)) {
    return(NULL)
  }
  return(paths[which(path_exists)[[1]]])
}

prep_binder_dockerfile <- function(dockerfile, root) {
  df <- readLines(dockerfile)
  from_idx <- grep("^FROM\\s+", df)
  if (length(from_idx) == 0) {
    stop("No FROM statement found in Dockerfile. Was it created with tugboat?")
  }
  # Hard-code the max R major version to 4 until rocker supports > 4
  r_major <- as.character(min(as.integer(R.Version()$major), 4))
  df[[from_idx[[1]]]] <- paste0("FROM rocker/binder:", r_major)
  binder_df_dir <- file.path(root, ".binder")
  if (!dir.exists(binder_df_dir)) {
    dir.create(binder_df_dir)
  }
  df <- c(df, "COPY --chown=${NB_USER} . /home/rstudio")
  writeLines(df, file.path(binder_df_dir, "Dockerfile"))
}

#' Create Binder-Compatible Docker Configuration for a tugboat Project
#'
#' The `binderize()` function converts an existing tugboat project into a
#' [Binder](https://mybinder.org)–compatible project by creating a Dockerfile
#' that launches RStudio Server via the `rocker/binder` base image.
#' Optionally, it can add a Binder launch badge to the project's README and
#' commit these changes automatically.
#'
#' This enables one-click, cloud-based execution of your R analysis environment
#' directly from GitHub using Binder.
#'
#' @details
#' The function assumes the specified Dockerfile resides in the root of a valid
#' Git repository (currently only GitHub repositories are supported). It generates
#' a Binder-compatible Dockerfile.
#'
#' If `add_readme_badge = TRUE`, a Binder badge will be appended to the README file,
#' linking directly to the live Binder instance.
#'
#' @param dockerfile Path to the tugboat-generated Dockerfile.
#' @param branch Character string specifying the Git branch, tag, or commit hash to build.
#'   Defaults to `"main"`.
#' @param hub The Binder hub to use. Currently only `"mybinder.org"` is supported.
#' @param urlpath The URL path to open inside the Binder instance.
#'   Defaults to `"rstudio"`, which opens an RStudio Server session.
#' @param add_readme_badge Logical. Whether to add a Binder launch badge to the README.
#'   Defaults to `TRUE`.
#' @param commit_changes Logical. Whether to automatically commit local Binder-related changes.
#'   If `TRUE`, the function will attempt to commit changes and instruct the
#'   user to push them before launching Binder. Defaults to `TRUE`.
#'
#' @return Invisibly returns `NULL`. Called primarily for its side effects of creating
#'   Binder-related files and optionally committing them.
#'
#' @note
#' Binder can only build from the remote GitHub repository.
#' The `.binder/Dockerfile` and README changes must be committed and pushed before
#' launching Binder; otherwise, the build will not reflect local modifications.
#'
#' @seealso
#' * [tugboat::create()] — Generates a Dockerfile from an analysis directory.
#' * [tugboat::build()] — Builds the corresponding Docker image locally.
#'
#' @examples
#' \dontrun{
#' # Create a Binder-compatible RStudio environment for your project
#' binderize(
#'   dockerfile = here::here("Dockerfile"),
#'   branch = "main",
#'   add_readme_badge = TRUE,
#'   commit_changes = TRUE
#' )
#' }
#'
#' @export
binderize <- function(
  dockerfile = here::here("Dockerfile"),
  branch = "main",
  hub = "mybinder.org",
  urlpath = "rstudio",
  add_readme_badge = TRUE,
  commit_changes = TRUE
) {
  hub <- match.arg(hub, c("mybinder.org")) # Add more hubs if interested later
  check_if_installed("gert")

  git_remotes <- gert::git_remote_list(dockerfile)
  git_remote <- git_remotes$url[git_remotes$name == "origin"][[1]]
  local_repo <- gert::git_find(dockerfile)
  username_repo <- strsplit(
    sub(".*github.com[:/](.*)\\.git$", "\\1", git_remote),
    "/"
  )[[1]]
  if (grepl("github.com", git_remote)) {
    binder_url <- sprintf(
      "https://%s/v2/gh/%s/%s?urlpath=%s",
      hub,
      paste(username_repo, collapse = "/"),
      branch,
      urlpath
    )
  } else {
    stop("Only GitHub repositories are supported currently")
  }
  badge_url <- sprintf("https://%s/badge_logo.svg", hub)

  prep_binder_dockerfile(dockerfile, local_repo)
  if (add_readme_badge) {
    check_if_installed("usethis")
    usethis::use_badge("Launch RStudio Binder", binder_url, badge_url)
  }
  if (commit_changes) {
    commit_files <- file.path(local_repo, ".binder/Dockerfile")
    if (add_readme_badge) {
      readme_path <- path_first_existing(usethis::proj_path(c("README.Rmd", "README.md")))
      commit_files <- c(commit_files, readme_path)
    }
    tryCatch({
      gert::git_add(commit_files)
      gert::git_commit("Adding Binder support")
      message("Changes committed. Push changes and then launch Binder at: ", binder_url)
    },
    error = function(e) {
      message("Automatic commit failed. Commit and push changes manually, then launch Binder at: ", binder_url)
    })
  } else {
    message("Binder files created locally. Commit and push changes manually, then launch Binder at: ", binder_url)
  }
  return(invisible(NULL))
}
