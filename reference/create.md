# Create a Dockerfile

This function will crawl all files in the current project/directory and
(attempt to) detect all R packages and store these in a lockfile. From
this lockfile, it will create a corresponding Dockerfile. It will also
copy the full contents of the current directory/project into the Docker
image. The directory in the Docker container containing the current
directory contents will be /current-directory-name. For example if your
analysis directory is named `incredible_analysis`, the corresponding
location in the generated Docker image will be `/incredible_analysis`.

## Usage

``` r
create(
  project = here::here(),
  as = file.path(project, "Dockerfile"),
  FROM = NULL,
  ...,
  exclude = NULL,
  verbose = FALSE,
  optimize_pak = TRUE
)
```

## Arguments

- project:

  The project directory. If no project directory is provided, by
  default, the here package will be used to determine the active
  project. If no project is currently active, then here defaults to the
  working directory where initially called.

- as:

  The file path to write to. The default value is
  `file.path(project, "Dockerfile")`.

- FROM:

  Docker image to start FROM. Default is FROM r-base:R.version.

- ...:

  Additional arguments which are passed directly to
  [renv::snapshot](https://rstudio.github.io/renv/reference/snapshot.html).
  Please see the documentation for that function for all relevant
  details.

- exclude:

  A vector of strings specifying all paths (files or directories) that
  should NOT be included in the Docker image. By default, all files in
  the directory will be included. NOTE: the file and directory paths
  should be relative to the project directory. They do NOT need to be
  absolute paths.

- verbose:

  A boolean indicating whether or not to print the resulting Dockerfile
  to the console. Default value is `FALSE`.

- optimize_pak:

  A boolean indicating whether or not to try to optimize package
  installations with pak. Defaults to `TRUE`. This should rarely be
  changed from its default value. However, sometimes this optimization
  may cause build failures. When encountering a build error, a good
  first step can be to set `optimize_pak = FALSE` and see if the error
  persists.

## Value

The Dockerfile contained as a string vector. Each vector element
corresponds to a line in the Dockerfile.

## See also

[here::here](https://here.r-lib.org/reference/here.html); this will be
used by default to determine the current project directory.

[renv::snapshot](https://rstudio.github.io/renv/reference/snapshot.html)
which this function relies on to find all R dependencies and create a
corresponding lockfile.

## Examples

``` r
if (FALSE) { # \dontrun{
# Create a Dockerfile based on the rocker/rstudio image.
# Write the Dockerfile locally to here::here("Dockerfile").
# Copy all files except the /data and /examples directories.
dock <- create(
  project = here::here(),
  FROM = "rocker/rstudio",
  exclude = c("/data", "/examples")
)
} # }
```
