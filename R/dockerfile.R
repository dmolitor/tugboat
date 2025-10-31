dockerfile <- function(lockfile, FROM = NULL, optimize_pak = TRUE) {
  lock <- renv::lockfile_read(lockfile)
  Rversion <- lock$R$Version
  if (!is.null(lock$Packages$renv$Version)) {
    renv_version <- paste0("renv@", lock$Packages$renv$Version)
  } else {
    renv_version <- "renv"
  }
  if (is.null(FROM)) FROM <- paste0("posit/r-base:", R.Version()$major, ".", R.Version()$minor, "-noble")
  if (!optimize_pak) {
    pak_setup <- paste0("RUN R -e \"pak::pkg_install('", renv_version, "')\"")
  } else {
    pak_setup <- paste0(
      "RUN R -e \"dist <- pak::system_r_platform_data()[['distribution']]; rel <- pak::system_r_platform_data()[['release']]; binary_url <- subset(pak::ppm_platforms(), distribution == dist & release == rel)[['binary_url']][1]; cran_binary_url <- if (!is.na(binary_url)) { sprintf('%s/__linux__/%s/latest', pak::ppm_repo_url(), binary_url)  } else { NA }; if (!is.na(cran_binary_url)) { pak::repo_add(CRAN = cran_binary_url) }; ",
      paste0("pak::pkg_install('", renv_version, "')"),
      "; if (!is.na(cran_binary_url)) { lf <- renv::lockfile_modify(repos = c('CRAN' = cran_binary_url)); tryCatch({ renv::lockfile_write(lf, './renv.lock') }, error = function(e) { invisible(NULL) }) }\""
    )
  }
  dock <- c(
    paste("FROM", FROM),
    paste("COPY", basename(lockfile), "renv.lock"),
    "RUN for d in /usr/local/lib/R/etc /usr/lib/R/etc; do \\",
    "      mkdir -p \"$d\" 2>/dev/null || true; \\",
    "      f=\"$d/Rprofile.site\"; \\",
    "      { echo \"options(renv.config.pak.enabled = TRUE)\" >> \"$f\" 2>/dev/null || true; } \\",
    "    done",
    "RUN R -e \"install.packages('pak', repos = sprintf('https://r-lib.github.io/p/pak/stable/%s/%s/%s', .Platform[['pkgType']], R.Version()[['os']], R.Version()[['arch']]))\"",
    pak_setup,
    "RUN R -e \"renv::restore()\""
  )
  return(dock)
}