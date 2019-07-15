from setuptools import setup, find_packages

setup(
    name="LexImpact Server",
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
        "flask-cors >= 3.0.7, < 3.1.0",
        "gunicorn >= 19.0.0, < 20.0.0",
        "openfisca-core >= 34.2.8, < 35.0.0",
        "openfisca-france >= 48.0.0, < 49.0.0",
        "pandas >= 0.24.0, < 0.25.0",
        "pyjwt >= 1.7.1, < 2.0.0",
        "toolz >= 0.9.0, < 1.0.0",
    ],
    extras_require={
        "dev": [
            "autopep8 >= 1.4.0, < 1.5.0",
            "black",
            "flake8 >= 3.7.0, < 3.8.0",
            "flake8-bugbear >= 19.3.0, < 20.0.0",
            "mock >= 3.0.5, < 4.0.0",
            "pytest >= 4.0.0, < 5.0.0",
            "pytest-mock >= 1.10.4, < 2.0.0",
            "python-dotenv >= 0.10.3, < 1.0.0",
            "snakeviz >= 2.0.0, < 3.0.0",
            "tables >= 3.4.0, < 3.5.0",
        ]
    },
    packages=find_packages(exclude=["tests*"]),
)
