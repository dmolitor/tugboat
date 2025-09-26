test_that("Expected installed packages are in the Docker image", {
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
  
  image_name <- build(
    dockerfile = here::here("examples/simple/Dockerfile"),
    image_name = "tugboat_simple",
    platforms = "linux/amd64",
    build_context = here::here("examples/simple")
  )
  # Check installed packages
  image_packages <- system(
    paste0(
      "docker run --rm --platform linux/amd64 ",
      image_name,
      " Rscript -e 'sort(row.names(installed.packages()))'"
    ),
    intern = TRUE
  )
  image_packages <- gsub("\\[\\d+\\]", "", image_packages)
  image_packages <- unlist(strsplit(gsub('"', "", paste(image_packages, collapse = " ")), "\\s+"))
  image_packages <- image_packages[image_packages != ""]

  testthat::expect_equal(image_name, "tugboat_simple:latest")
  testthat::expect_in(
    c("jsonlite", "renv", "rprojroot", "stringi", "withr"),
    image_packages
  )
})

test_that("Dockerfile in a different directory than build context works correctly", {
  testthat::skip_on_cran()
  if (!interactive()) {
    skip("Tests only run interactively")
  }

  if (file.exists(here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"))) {
    file.remove(here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"))
  }
  exclude <- c("./mtcars.csv")
  dock <- create(
    project = here::here("examples/diff_dockerfile_and_context/"),
    as = here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"),
    FROM = paste0("posit/r-base:", R.version$major, ".", R.version$minor, "-noble"),
    exclude = exclude
  )

  # Build the docker image
  image_name <- build(
    dockerfile = here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"),
    image_name = "tugboat_diff_df_context",
    platforms = "linux/arm64",
    build_context = here::here("examples/diff_dockerfile_and_context/")
  )

  # Check copied files
  files <- system(
    paste0(
      "docker run --rm --platform linux/arm64 ",
      image_name,
      " ls -la /diff_dockerfile_and_context"
    ),
    intern = TRUE
  ) |> strsplit(split = " ") |> 
    (\(x) lapply(x, \(y) y[[length(y)]]))() |>
    unlist()

  # Ensure that only expected files are included
  testthat::expect_false(exclude %in% files)
})

test_that("Non-Ubuntu image works correctly", {
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
      FROM = paste0("posit/r-base:", R.version$major, ".", R.version$minor, "-bookworm-amd64"),
      exclude = c("run.R")
    )
  })
  image_name <- build(
    dockerfile = here::here("examples/simple/Dockerfile"),
    image_name = "tugboat_simple_bookworm",
    platforms = "linux/amd64",
    build_context = here::here("examples/simple")
  )
  # Check installed packages
  image_packages <- system(
    paste0(
      "docker run --rm --platform linux/amd64 ",
      image_name,
      " Rscript -e 'sort(row.names(installed.packages()))'"
    ),
    intern = TRUE
  )
  image_packages <- gsub("\\[\\d+\\]", "", image_packages)
  image_packages <- unlist(strsplit(gsub('"', "", paste(image_packages, collapse = " ")), "\\s+"))
  image_packages <- image_packages[image_packages != ""]

  testthat::expect_equal(image_name, "tugboat_simple_bookworm:latest")
  testthat::expect_in(
    c("jsonlite", "renv", "rprojroot", "stringi", "withr"),
    image_packages
  )
})
