test_that("Creating a Dockerfile works as expected", {
  testthat::skip_on_cran()
  if (!interactive()) {
    skip("Tests only run interactively")
  }

  system("docker system prune -a --force")
  
  if (file.exists(here::here("examples/simple/Dockerfile"))) {
    file.remove(here::here("examples/simple/Dockerfile"))
  }
  if (file.exists(here::here("examples/simple/renv.lock"))) {
    file.remove(here::here("examples/simple/renv.lock"))
  }
  # Create the Dockerfile
  dock <- suppressWarnings({
    create(project = here::here("examples/simple"), FROM = "rocker/r-ver")
  })
  # Read the lockfile
  lockfile <- renv::lockfile_read(here::here("examples/simple/renv.lock"))
  # Ensure that lockfile has all the correct dependencies
  testthat::expect_equal(
    names(lockfile$Packages),
    c("jsonlite", "renv", "rprojroot", "stringi", "withr")
  )
})
