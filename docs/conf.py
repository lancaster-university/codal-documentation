# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import subprocess
import os
import textwrap

# Utility Functions
def genInputString( libraries ):
    buffer = []
    for lib in libraries:
        #buffer.append( F"\"{os.path.join( '..', 'libraries', lib, 'inc' )}\"" )
        buffer.append( F"\"{os.path.join( '..', 'libraries', lib, 'source' )}\"" ) # This will complain if we have duplicated documentation!
    return ' '.join(buffer)

def getGitVersion( library ):
    result = subprocess.run(
        ['git', 'describe', '--tags'],
        cwd=os.path.join( '..', 'libraries', library ),
        stdout=subprocess.PIPE
    )
    return result.stdout.decode('UTF-8').strip()

# -- Project information -----------------------------------------------------

codal_libraries = [ 'codal-microbit-v2', 'codal-core' ]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'CODAL Documentation'
copyright = '2023, John Vidler'
author = 'John Vidler'
release = getGitVersion( 'codal-microbit-v2' ) # The full version, including alpha/beta/rc tags

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'breathe',
    'exhale',
    'sphinx.ext.githubpages',
    'sphinx.ext.todo'
]

todo_include_todos = True

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
    # Set to true to see the doxygen commands in the build log
    "verboseBuild": False,
    #"exhaleDoxygenStdin":    "INPUT = ../../libraries/codal-microbit-v2 ../../libraries/codal-core",
    "exhaleDoxygenStdin":    textwrap.dedent(F'''
        INPUT = {genInputString(codal_libraries)}
        ENABLE_PREPROCESSING   = YES
        MACRO_EXPANSION        = YES
        SEARCH_INCLUDES        = YES
        SKIP_FUNCTION_MACROS   = YES
        PREDEFINED += DOXYGEN_SHOULD_SKIP_THIS
    '''),
}

# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp'

#templates_path = ['_templates']
exclude_patterns = ['_doxygen', '_env', '_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = F'{project} {release}'
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_theme_options = {
    "repository_url": "https://github.com/lancaster-university/codal-documentation",
    "use_repository_button": True,
    "home_page_in_toc": True,
    "show_toc_level": 0,
    "use_download_button": False,
    "default_mode": "light",
    "announcement": "We're currently porting the DAL documentation over to CODAL. The information on here may be outdated or incorrect!",
}

#html_sidebars = {
#    "**": ["sidebar-logo.html", "search-field.html", "sbt-sidebar-nav.html"]
#}