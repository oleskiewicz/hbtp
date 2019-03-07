#!/usr/bin/env python3
import os

import setuptools

with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.rst")
) as f:
    long_description = f.read()

setuptools.setup(
    name="hbtp",
    version="0.1",
    author="Piotr Oleskiewicz",
    author_email="piotr.oleskiewicz@durham.ac.uk",
    description=(
        """
        A set of tools for reading and analysing halo catalogues in HBTplus
        format"
    """
    ),
    long_description=long_description,
    long_description_content_type="text/rst",
    license="GPLv3",
    keywords="hbtplus cosmology astrophysics dark_matter halo_finder",
    url="https://github.com/oleskiewicz/hbtp",
    packages=["hbtp"],
    install_requires=[
        l.strip()
        for l in open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "requirements.txt"
            )
        ).readlines()
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research"
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
