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
import os
import sys
# sys.path.insert(0, os.path.abspath('.'))

import subprocess

list_files = subprocess.Popen(["cd", "src/geocat/f2py/fortran"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "dpres_plevel_dp.pyf", "dpres_plevel_dp.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "grid2triple.pyf", "grid2triple.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "linint2.pyf", "linint2.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "moc_loops.pyf", "moc_loops.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "rcm2points.pyf", "rcm2points.f", "rcm2rgrid.f", "linmsg_dp.f", "linint2.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "rcm2rgrid.pyf", "rcm2rgrid.f", "linmsg_dp.f", "linint2.f"])
list_files = subprocess.Popen(["f2py", "-c", "--fcompiler=gnu95", "triple2grid.pyf", "triple2grid.f"])
list_files = subprocess.Popen(["cd", "../../../.."])
list_files = subprocess.Popen(["python", "-m", "pip", "install", ".", "--no-deps", "-vv"])

# result = subprocess.run(['/bin/bash', '/home/user1/myfile.run'], stdout=subprocess.PIPE)

subprocess.call(['sh', './build.sh'])

# process = subprocess.Popen(['./build.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# process.wait() # Wait for process to complete.
#
# # iterate on the stdout line by line
# for line in process.stdout.readlines():
#     print(line)
#
import geocat.f2py

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import Mock as MagicMock


class Mock(MagicMock):

    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = ["xarray", "dask", "dask.array", "dask.array.core"]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx', 'sphinx.ext.mathjax'
]

#mathjax_path = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"

intersphinx_mapping = {
    'dask': ('https://docs.dask.org/en/latest/', None),
    'python': ('http://docs.python.org/3/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'xarray': ('http://xarray.pydata.org/en/stable/', None),
}

napoleon_use_admonition_for_examples = True
napoleon_include_special_with_doc = True

autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# # Add any paths that contain custom static files (such as style sheets) here,
# # relative to this directory. They are copied after the builtin static files,
# # so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
#
# # List of patterns, relative to source directory, that match files and
# # directories to ignore when looking for source files.
# # This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
#
# # If true, `todo` and `todoList` produce output, else they produce nothing.
# todo_include_todos = False


# -- Project information -----------------------------------------------------

project = 'GeoCAT-f2py'

import datetime

current_year = datetime.datetime.now().year
copyright = u'{}, University Corporation for Atmospheric Research'.format(
    current_year)
author = u'GeoCAT'

# The version info for the project being documented
def read_version():
    for line in open('../meta.yaml').readlines():
        index = line.find('version')
        if index > -1:
            return line[index + 8:].replace('\'', '').strip()

# The short X.Y version.
version = read_version()

# The full version, including alpha/beta/rc tags.
release = read_version()

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

#html_theme = 'alabaster'
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    html_theme = 'default'
else:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_static/images/nsf.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'geocat-f2pydoc'