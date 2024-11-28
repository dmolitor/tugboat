# Load tugboat
devtools::load_all(here::here())

# Create the Dockerfile
dock <- create(
  project = here::here("examples/bolasso"),
  FROM = "rocker/rstudio",
  as = here::here("examples/bolasso/Dockerfile"),
  exclude = c("run.R")
)

# Build the image
image_name <- build(
  dockerfile = here::here("examples/bolasso/Dockerfile"),
  image_name = "tugboat_bolasso",
  platforms = "linux/arm64",
  build_context = here::here("examples/bolasso")
)

# Run the image
system(
  "docker run --rm -ti -e DISABLE_AUTH=true -e ROOT=true -p 8787:8787 tugboat_bolasso:latest",
  receive.console.signals = TRUE
)
# Open the following url in your browser: http://localhost:8787