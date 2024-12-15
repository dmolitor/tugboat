test_that("Expected installed packages are in the Docker image", {
  testthat::skip_on_cran()
  if (!interactive() && Sys.info()[["sysname"]] != "Linux") {
    skip("Tests only run interactively or on Ubuntu (Linux)")
  }
  
  image_name <- build(
    dockerfile = here::here("examples/simple/Dockerfile"),
    image_name = "tugboat_simple",
    platforms = "linux/arm64",
    build_context = here::here("examples/simple")
  )
  # Check installed packages
  image_packages <- system(
    paste0(
      "docker run --rm ",
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
  if (!interactive() && Sys.info()[["sysname"]] != "Linux") {
    skip("Tests only run interactively or on Ubuntu (Linux)")
  }

  if (file.exists(here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"))) {
    file.remove(here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"))
  }
  exclude <- c("./mtcars.csv")
  dock <- create(
    project = here::here("examples/diff_dockerfile_and_context/"),
    as = here::here("examples/diff_dockerfile_and_context/docker/Dockerfile"),
    FROM = "r-base",
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
      "docker run --rm ",
      image_name,
      " ls -la /diff_dockerfile_and_context"
    ),
    intern = TRUE
  ) |> strsplit(split = " ") |> 
    (\(x) lapply(x, \(y) y[[length(y)]]))() |>
    unlist()

  # Ensure that all expected packages are installed
  testthat::expect_false(exclude %in% files)
})
