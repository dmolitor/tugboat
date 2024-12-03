test_that("Creating a Dockerfile works as expected", {
  testthat::skip_on_ci()
  testthat::skip_on_cran()
  if (file.exists(here::here("examples/simple/Dockerfile"))) {
    file.remove(here::here("examples/simple/Dockerfile"))
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
