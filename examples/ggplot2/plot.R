library(ggplot2)

df <- read.csv("/ggplot2/data/mtcars.csv")

ggplot(df, aes(x = hp, y = wt, color = factor(cyl))) +
  geom_point() +
  facet_wrap(~ factor(am), nrow = 3)

ggsave("/ggplot2/figures/mtcars.png", height = 4, width = 6)
