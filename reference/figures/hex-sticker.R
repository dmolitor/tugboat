library(hexSticker)
library(magick)

img <- image_read(here::here("man", "figures", "tugboat-logo.jpg"))
img <- img |>
  image_convert("png") |>
  image_fill(color = "none") |>
  image_annotate(
    text = "tugboat",
    font = "Brush Script MT",
    style = "normal",
    weight = 1000,
    size = 70,
    location = "+165+390",
    color = "gray30"
)

sticker(
  filename = here::here("man", "figures", "logo.png"),
  white_around_sticker = TRUE,
  img,
  package = "",
  s_x = 1.05,
  s_y = 1.2,
  s_width = 2,
  s_height = 14,
  h_fill = "white",
  h_color = "#A9A9A9"
)


# Remove the background at remove.bg