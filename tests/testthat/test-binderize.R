test_that("Binderizing project works as expected", {
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

  dock <- create(
    project = here::here("examples/simple/"),
    FROM = paste0("posit/r-base:", R.version$major, ".", R.version$minor, "-jammy"),
    exclude = c("run.R")
  )

  expect_error(binderize(here::here("Dockerfile"))) # No Dockerfile exists here
  expect_no_error(binderize(here::here("examples/simple/Dockerfile"), add_readme_badge = FALSE))
  expect_message(
    binderize(here::here("examples/simple/Dockerfile"), add_readme_badge = FALSE), 
    regexp = "Your repository has been configured for Binder"
  )
  if (dir.exists(here::here(".binder"))) {
    file.remove(here::here(".binder/Dockerfile"))
    file.remove(here::here(".binder/"))
  }
})