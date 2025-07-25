library(metafor)   # random‑effects models
library(readr)

dat <- read_csv("../../data_lit/extracted_studies.csv")

# calcula Hedges g
dat <- escalc(measure="SMD",
              m1i = mean_gifted, sd1i = sd_gifted, n1i = n_gifted,
              m2i = mean_control, sd2i = sd_control, n2i = n_control,
              data = dat)

res <- rma(yi, vi, data = dat, method = "DL")
forest(res, slab = paste(dat$Author, dat$Year))