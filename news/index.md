# Changelog

## tugboat 0.1.6

- Resolves [\#18](https://github.com/dmolitor/tugboat/issues/18).
  Previously, when calling
  [`binderize()`](https://dmolitor.com/tugboat/reference/binderize.md),
  tugboat would never overwrite an existing Dockerfile at
  `.binder/Dockerfile` if it already existed. This is bad if the user
  has updated the tugboat Dockerfile and wants to update the Binder
  Dockerfile correspondingly. Now, tugboat will default to overwriting
  the existing Binder Dockerfile, ensuring that any changes in the
  tugboat Dockerfile will propagate to Binder. The user can explicitly
  control this behavior via the `overwrite` argument of `binderize`.

## tugboat 0.1.5

CRAN release: 2025-11-10

- Resolves [\#17](https://github.com/dmolitor/tugboat/issues/17). This
  was a Windows-specific issue where RStudio would lock down the .Rproj
  file, causing `docker buildx build` to fail.

- Adds a `verbose` argument to
  [`build()`](https://dmolitor.com/tugboat/reference/build.md). This
  will print the full build call that is being executed. This can
  potentially be helpful when debugging build errors.

- Resolves [\#16](https://github.com/dmolitor/tugboat/issues/16). This
  provides slightly more efficient Binder builds and handles build
  errors more cleanly.

## tugboat 0.1.4

CRAN release: 2025-10-31

- Adds preliminary Binder support. See the new
  [`binderize()`](https://dmolitor.com/tugboat/reference/binderize.md)
  function and its corresponding documentation.

- Adds a new argument `optimize_pak = TRUE` to the
  [`create()`](https://dmolitor.com/tugboat/reference/create.md)
  function. This argument should almost never need to be set to FALSE,
  but in some cases our method of optimizing package installation with
  pak can fail, in which case setting `optimize_pak = FALSE` reverts to
  the older, more fail-proof method and can alleviate those issues.

## tugboat 0.1.3

CRAN release: 2025-09-27

- Added better support for binaries via `pak`. Still some limitations
  when using less common Linux distributions (e.g. Alpine) or older
  distributions (e.g. Debian 11). However, for up-to-date Debian and
  Ubuntu distributions, this should be fairly seemless and should result
  in potentially huge installation speedups. See [PPM
  documentation](https://packagemanager.posit.co/__docs__/admin/serving-binaries.html)
  and [related GitHub
  issues](https://github.com/hadley/r-in-production/issues/22) for some
  light bedtime reading on this subject.

## tugboat 0.1.2

- Added argument `verbose` to the
  [`tugboat::create()`](https://dmolitor.com/tugboat/reference/create.md)
  function. If `verbose = TRUE`, the resulting Dockerfile will be
  printed to the R console.

## tugboat 0.1.1

CRAN release: 2024-12-17

- In
  [`tugboat::build()`](https://dmolitor.com/tugboat/reference/build.md)
  the default value for the build_context is now
  `build_context = here::here()` instead of
  `build_context = dirname(dockerfile)`. This resolves a potential issue
  where, if the user saves the Dockerfile in a different directory than
  the build context,
  [`tugboat::build()`](https://dmolitor.com/tugboat/reference/build.md)
  incorrectly infers the build context as the directory containing the
  Dockerfile. Now
  [`tugboat::build()`](https://dmolitor.com/tugboat/reference/build.md)
  will infer the build context as the current project directory
  regardless of the Dockerfile location. As always, the user can
  explicitly specify both of these arguments to override the default
  values.

- [`tugboat::create()`](https://dmolitor.com/tugboat/reference/create.md)
  will now execute
  [`renv::install()`](https://rstudio.github.io/renv/reference/install.html)
  before
  [`renv::snapshot()`](https://rstudio.github.io/renv/reference/snapshot.html)
  when running in non-interactive mode. This resolves the issue where
  [`renv::snapshot()`](https://rstudio.github.io/renv/reference/snapshot.html)
  won’t snapshot packages that are not installed when being run
  non-interactively, thus potentially leaving essential packages out of
  the Docker image.

- tugboat no longer relies on the dockerfiler package. This allows
  support for a much wider range of base images and minimizes the
  dependencies for tugboat.

## tugboat 0.1.0

CRAN release: 2024-12-09

- Initial CRAN submission.
