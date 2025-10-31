test_that("Creating a Dockerfile works as expected", {
  testthat::skip_on_cran()
  if (!interactive()) {
    skip("Tests only run interactively")
  }
  
  if (file.exists(here::here("examples/simple/Dockerfile"))) {
    file.remove(here::here("examples/simple/Dockerfile"))
  }
  if (file.exists(here::here("examples/simple/renv.lock"))) {
    file.remove(here::here("examples/simple/renv.lock"))
  }
  # Create the Dockerfile
  dock <- suppressWarnings({
    create(
      project = here::here("examples/simple"),
      FROM = paste0("posit/r-base:", R.version$major, ".", R.version$minor, "-opensuse156")
    )
  })
  # Read the lockfile
  lockfile <- renv::lockfile_read(here::here("examples/simple/renv.lock"))
  # Ensure that lockfile has all the correct dependencies
  testthat::expect_equal(
    names(lockfile$Packages),
    c("jsonlite", "renv", "rprojroot", "stringi", "withr")
  )
})

test_that("Creating a non-optimized Dockerfile works as expected", {
  testthat::skip_on_cran()
  if (!interactive()) {
    skip("Tests only run interactively")
  }
  
  if (file.exists(here::here("examples/simple/Dockerfile"))) {
    file.remove(here::here("examples/simple/Dockerfile"))
  }
  if (file.exists(here::here("examples/simple/renv.lock"))) {
    file.remove(here::here("examples/simple/renv.lock"))
  }
  # Create the Dockerfile
  dock <- suppressWarnings({
    create(
      project = here::here("examples/simple"),
      FROM = paste0("posit/r-base:", R.version$major, ".", R.version$minor, "-opensuse156"),
      optimize_pak = FALSE
    )
  })
  # Basically just make sure that it just has a vanilla pak install of renv
  expect_true(startsWith(dock[[9]], "RUN R -e \"pak::pkg_install('renv@"))
})