# CODAL Documentation

[![Build Natively](https://github.com/lancaster-university/codal-documentation/actions/workflows/build-documentation.yml/badge.svg?branch=master)](https://github.com/lancaster-university/codal-documentation/actions/workflows/build-documentation.yml)

[DIRECT LINK TO THE CURRENT DOCUMENTATION](https://lancaster-university.github.io/codal-documentation/)

## About

This repository is the source for the documentation at https://lancaster-university.github.io/codal-documentation/ and automatically builds the site on updates to the master branch.

## Contributing

We're actively looking for contributions, and will accept pull requests for:

- Source code documentation (in their respective repositories)
- Example Projects
- Hardware guides

To contribute to the API documentation, please consider submitting a PR to one of the following repositories, as these are the current focus for the project:

- https://github.com/lancaster-university/codal-core
- https://github.com/lancaster-university/codal-microbit-v2

Other codal-related documentation PRs will be considered, but may take a while to be reviewed.

## Bugs and/or Errors

If you find documentation errors, please file issues for this in this repository!

## Building Locally

To build the documentation locally, the following prerequisites must be present:

- The arm-none-eabi-* tool suite
- cmake
- make
- doxygen
- python 3+
    - sphinx-build
    - sphinx-book-theme

Ensure that you can build CODAL normally by running `./build.py` from the repository root, then if this completes, move to the `docs` subdirectory and run `make html` to build the full HTML documentation.

> Note that if you experience strange desynchronisation between the HTML output and the documentation sources, you may need to run `make clean` and `make html` again. This generally manifests in the navigation not updating for pages deep in the heirachy.