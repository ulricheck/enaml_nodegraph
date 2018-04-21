#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.core import setup, Extension
import numpy


setup(name = "enaml_nodegraph",
      version = '0.1',
      description = "Nodegraph Editor for enaml",
      author = "Ulrich Eck",
      author_email = "ulrich.eck@tum.de",
      url = "https://github.com/ulricheck/enaml_nodegraph",
      packages = find_packages('.'),
      package_data = {'enaml_nodegraph' : ['views/*.enaml']},
      license = "BSD License",
      requires=[
        'atom',
        'enaml',
      ],
      zip_safe=False,
      long_description = """\
Nodegraph Editor for enaml applications""",
      classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      )