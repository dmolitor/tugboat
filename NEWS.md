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
