# Load tugboat
devtools::load_all(here::here())

# Create the Dockerfile
dock <- create(project = here::here("examples/simple"), FROM = "rocker/r-ver")

# Build the docker image
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

# Ensure that all expected packages are installed
testthat::expect_in(
  c("jsonlite", "renv", "rprojroot", "stringi", "withr"),
  image_packages
)
