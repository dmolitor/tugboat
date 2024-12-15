# Load tugboat
devtools::load_all(here::here())

# Create the Dockerfile
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
