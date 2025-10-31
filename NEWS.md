# tugboat 0.1.4

- Adds preliminary Binder support. See the new `binderize()` function and
its corresponding documentation.

- Adds a new argument `optimize_pak = TRUE` to the `create()` function.
This argument should almost never need to be set to FALSE, but in some cases
our method of optimizing package installation with pak can fail, in which
case setting `optimize_pak = FALSE` reverts to the older, more fail-proof
method and can alleviate those issues.

# tugboat 0.1.3

- Added better support for binaries via `pak`. Still some limitations when
using less common Linux distributions (e.g. Alpine) or older distributions
(e.g. Debian 11). However, for up-to-date Debian and Ubuntu distributions,
this should be fairly seemless and should result in potentially huge
installation speedups. See [PPM documentation](https://packagemanager.posit.co/__docs__/admin/serving-binaries.html)
and [related GitHub issues](https://github.com/hadley/r-in-production/issues/22)
for some light bedtime reading on this subject.

# tugboat 0.1.2

- Added argument `verbose` to the `tugboat::create()` function. If
`verbose = TRUE`, the resulting Dockerfile will be printed to the R console.

# tugboat 0.1.1

- In `tugboat::build()` the default value for the build_context is now
`build_context = here::here()` instead of `build_context = dirname(dockerfile)`.
This resolves a potential issue where, if the user saves the Dockerfile in a
different directory than the build context, `tugboat::build()` incorrectly infers
the build context as the directory containing the Dockerfile. Now `tugboat::build()`
will infer the build context as the current project directory regardless
of the Dockerfile location. As always, the user can explicitly specify
both of these arguments to override the default values.

- `tugboat::create()` will now execute `renv::install()` before `renv::snapshot()`
when running in non-interactive mode. This resolves the issue where
`renv::snapshot()` won't snapshot packages that are not installed when
being run non-interactively, thus potentially leaving essential packages out of
the Docker image.

- tugboat no longer relies on the dockerfiler package. This allows support for a
much wider range of base images and minimizes the dependencies for tugboat.

# tugboat 0.1.0

* Initial CRAN submission.
