# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
import pip
from setuptools import setup

# Load requirements list from 'requirements.txt'
install_reqs = pip.req.parse_requirements("requirements.txt", session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('axiom/axiom.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "cmdline-axiom",
    packages = ["axiom"],
    package_data={'axiom': ['data/*.xml']},
    entry_points = {
        "console_scripts": ['axiom = axiom.axiom:main']
        },
    install_requires = reqs,
    version = version,
    description = "Python command line application bare bones template.",
    long_description = long_descr,
    author = "Jan-Philip Gehrcke,Nithin Philips",
    author_email = "jgehrcke@googlemail.com,nithin@nithinphilips.com",
    url = "http://gehrcke.de/2014/02/distributing-a-python-command-line-application",
    )
