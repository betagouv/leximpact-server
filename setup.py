# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="LexImpact",
    author="LexImpact Team",
    author_email="leximpact@openfisca.org",
    version="0.1.0",
    license="https://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/betagouv/leximpact",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: French",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    install_requires=[
        "connexion[swagger-ui] >= 2.2.0, < 3.0.0",
        "dash >= 0.39.0, < 0.40.0",
        "dash-daq >= 0.1.0, < 0.2.0",
        "openfisca-core >= 29.0.0, < 30.0.0",
        "openfisca-france >= 38.0.0, < 39.0.0",
        "pandas >= 0.24.0, < 0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest >= 4.0.0, < 5.0.0",
            "snakeviz >= 2.0.0, < 3.0.0",
            "tables >= 3.4.0, < 3.5.0",
        ]
    },
    packages=find_packages(exclude=["tests*"]),
)
