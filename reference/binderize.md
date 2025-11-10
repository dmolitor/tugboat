# Prepare project for Binder

The `binderize()` function converts an existing tugboat project into a
[Binder](https://mybinder.org)–compatible project by creating a
Dockerfile that launches RStudio Server via the `rocker/binder` base
image. Optionally, it can add a Binder launch badge to the project's
README.

## Usage

``` r
binderize(
  dockerfile = here::here("Dockerfile"),
  branch = "main",
  hub = "mybinder.org",
  urlpath = "rstudio",
  add_readme_badge = TRUE
)
```

## Arguments

- dockerfile:

  Path to the tugboat-generated Dockerfile.

- branch:

  Character string specifying the Git branch, tag, or commit hash to
  build. Defaults to `"main"`.

- hub:

  The Binder hub to use. Currently only `"mybinder.org"` is supported.

- urlpath:

  The URL path to open inside the Binder instance. Defaults to
  `"rstudio"`, which opens an RStudio Server session.

- add_readme_badge:

  Logical. Whether to add a Binder launch badge to the README. Defaults
  to `TRUE`.

## Value

Invisibly returns `NULL`. Called primarily for its side effects of
creating Binder-related files and optionally committing them.

## Details

This enables one-click, cloud-based execution of your R analysis
environment directly from GitHub using Binder.

Currently only GitHub repositories are supported. If
`add_readme_badge = TRUE`, a Binder badge will be appended to the README
file, linking to the live Binder instance.

## Note

Binder can only build from the remote GitHub repository. The
`.binder/Dockerfile` and README changes must be committed and pushed
before launching Binder; otherwise, the build will not reflect local
modifications.

## See also

- [`create()`](https://dmolitor.com/tugboat/reference/create.md) —
  Generates a Dockerfile from an analysis directory.

- [`build()`](https://dmolitor.com/tugboat/reference/build.md) — Builds
  the corresponding Docker image locally.

## Examples

``` r
if (FALSE) { # \dontrun{
binderize(
  dockerfile = here::here("Dockerfile"),
  branch = "main",
  add_readme_badge = TRUE
)
} # }
```
