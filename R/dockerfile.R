dockerfile <- function(lockfile, FROM = NULL) {
  lock <- renv::lockfile_read(lockfile)
  Rversion <- lock$R$Version
  if (!is.null(lock$Packages$renv$Version)) {
    renv_version <- paste0("renv@", lock$Packages$renv$Version)
  } else {
    renv_version <- "renv"
  }
  if (is.null(FROM)) FROM <- paste0("r-base:", Rversion)
  dock <- c(
    paste("FROM", FROM),
    paste("COPY", basename(lockfile), "renv.lock"),
    "RUN mkdir -p /usr/local/lib/R/etc/ /usr/lib/R/etc/ && \\",
    "    for f in /usr/local/lib/R/etc/Rprofile.site /usr/lib/R/etc/Rprofile.site; do \\\n      echo \"options(renv.config.pak.enabled = TRUE)\" >> \"$f\"; \\\n    done",
    "RUN R -e \"install.packages('pak', repos = sprintf('https://r-lib.github.io/p/pak/stable/%s/%s/%s', .Platform[['pkgType']], R.Version()[['os']], R.Version()[['arch']]))\"",
    paste0("RUN R -e \"dist <- pak::system_r_platform_data()[['distribution']]; rel <- pak::system_r_platform_data()[['release']]; binary_url <- subset(pak::ppm_platforms(), distribution == dist & release == rel)[['binary_url']][1]; cran_binary_url <- if (!is.na(binary_url)) { sprintf('%s/__linux__/%s/latest', pak::ppm_repo_url(), binary_url)  } else { NA }; if (!is.na(cran_binary_url)) { pak::repo_add(CRAN = cran_binary_url) }; ", paste0("pak::pkg_install('", renv_version, "')"), "; if (!is.na(cran_binary_url)) { renv::lockfile_modify(repos = c('CRAN' = cran_binary_url)) |> renv::lockfile_write('./renv.lock') }\""),
    "RUN R -e \"renv::restore()\""
  )
  return(dock)
}