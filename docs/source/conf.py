# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import subprocess
import os

# Utility Functions
def genInputString( libraries ):
    buffer = []
    for lib in libraries:
        buffer.append( F"\"{os.path.join( '..', '..', 'libraries', lib, 'inc' )}\"" )
        #buffer.append( F"\"{os.path.join( '..', '..', 'libraries', lib, 'source' )}\"" ) # This will complain if we have duplicated documentation!
    return ' '.join(buffer)

def getGitVersion( library ):
    result = subprocess.run(
        ['git', 'describe', '--tags'],
        cwd=os.path.join( '..', '..', 'libraries', library ),
        stdout=subprocess.PIPE
    )
    return result.stdout.decode('UTF-8').strip()

# -- Project information -----------------------------------------------------

codal_libraries = [ 'codal-microbit-v2', 'codal-core' ]

project = 'CODAL'
copyright = '2022, Microbit Foundation, Lancaster University'
author = 'Microbit Foundation, Lancaster University'

# The full version, including alpha/beta/rc tags
release = getGitVersion( 'codal-microbit-v2' )

html_title = F'{project} {release}'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'breathe',
    'exhale',
    'sphinx.ext.githubpages'
]

# Breathe Configuration (paths from the source/ subpath context)
breathe_projects = { "CODAL": "./_doxygen/xml" }
breathe_default_project = "CODAL"
#breathe_default_members = ('members', 'undoc-members')

# Setup the exhale extension
exhale_args = {
    # These arguments are required
    "containmentFolder":     "./api",
    "rootFileName":          "root.rst",
    "doxygenStripFromPath":  "..",
    # Heavily encouraged optional argument (see docs)
    "rootFileTitle":         "CODAL API",
    # Suggested optional arguments
    "createTreeView":        True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    "treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    #"exhaleDoxygenStdin":    "INPUT = ../../libraries/codal-microbit-v2 ../../libraries/codal-core",
    "exhaleDoxygenStdin":    F"INPUT = {genInputString(codal_libraries)}",
}

# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp'

# Add any paths that contain templates here, relative to this directory.
templates_path = [ 'templates' ]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'sphinx_material'
#html_theme_options = {
#    'globaltoc_depth': 2
#}
#html_sidebars = {
#    "**": ["globaltoc.html"]
#}

html_theme = 'sphinx_book_theme'
html_theme_options = {
    "repository_url": "https://github.com/lancaster-university/codal-documentation",
    "use_repository_button": True,
    "home_page_in_toc": True,
    "show_toc_level": 0,
    "use_download_button": False,
    "announcement": "We're currently porting the DAL documentation over to CODAL. The information on here may be outdated or incorrect!",
}

html_sidebars = {
    "**": ["sidebar-logo.html", "search-field.html", "sbt-sidebar-nav.html"]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [ 'static' ]

html_css_files = [
    'theme_mods.css',
]