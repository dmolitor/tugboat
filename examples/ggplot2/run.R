# Load tugboat
devtools::load_all(here::here())

# Create the Dockerfile
dock <- create(
  project = here::here("examples/ggplot2"),
  FROM = "rocker/r-ver",
  as = here::here("examples/ggplot2/Dockerfile"),
  exclude = c("data/mtcars_unnecessary.csv", "run.R")
)

# Build the image
image_name <- build(
  dockerfile = here::here("examples/ggplot2/Dockerfile"),
  image_name = "tugboat_ggplot2",
  platforms = "linux/arm64",
  build_context = here::here("examples/ggplot2")
)

# Run the plot.R script in the Docker container and save the plot locally
system(
  paste0(
    "docker run --rm -v ",
    here::here("examples/ggplot2/figures"),
    ":/ggplot2/figures ",
    image_name,
    " Rscript /ggplot2/plot.R"
  ),
  receive.console.signals = TRUE
)

# List all files in the container's /ggplot2/data directory
# If working correctly mtcars_unnecessary.csv should not be there
# Should only be mtcars.csv
system(
  paste0(
    "docker run --rm ",
    image_name,
    " ls -la /ggplot2/data"
  ),
  receive.console.signals = TRUE
)
