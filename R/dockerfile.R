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
    "RUN mkdir -p /usr/local/lib/R/etc/ /usr/lib/R/etc/",
    "RUN echo \"options(renv.config.pak.enabled = TRUE, repos = c(CRAN = 'https://cran.rstudio.com/'), download.file.method = 'libcurl', Ncpus = 4)\" | tee /usr/local/lib/R/etc/Rprofile.site | tee /usr/lib/R/etc/Rprofile.site",
    "RUN R -e \"install.packages('pak', repos = sprintf('https://r-lib.github.io/p/pak/stable/%s/%s/%s', .Platform[['pkgType']], R.Version()[['os']], R.Version()[['arch']]))\"",
    paste0("RUN R -e \"pak::pkg_install('", renv_version, "')\""),
    paste("COPY", basename(lockfile), "renv.lock"),
    paste("RUN R -e \"renv::restore()\"")
  )
  return(dock)
}