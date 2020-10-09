from setuptools import setup, find_packages  # type: ignore

basic_requirements = [
    "alembic >= 1.0.11, < 2.0.0",
    "connexion[swagger-ui] >= 2.6.0, < 3.0.0",
    "flask-cors >= 3.0.7, < 3.1.0",
    "gunicorn >= 20.0.0, < 21.0.0",
    "mailjet-rest >= 1.3.3, < 2.0.0",
    "numpy == 1.17",
    "pandas >= 0.24.0, < 0.25.0",
    "psycopg2 >= 2.8.3, < 3.0.0",
    "pyjwt >= 1.7.1, < 2.0.0",
    "python-dotenv >= 0.10.3, < 1.0.0",
    "sqlalchemy >= 1.3.5, < 2.0.0",
    "toolz >= 0.9.0, < 1.0.0",
]

impot_revenu_requirements = [
    "openfisca-france >= 48.10.6, < 49.0.0",
]

dotations_requirements = [
    "openfisca-france-dotations-locales >= 0.7.0, < 1.0.0",
]

setup(
    name="LexImpact Server",
    author="LexImpact Team",
    author_email="leximpact@openfisca.org",
    version="1.5.0",
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
        basic_requirements,
        impot_revenu_requirements,
        dotations_requirements
    ],
    extras_require={
        "dev": [
            "pycodestyle<2.6.0,>=2.5.0",
            "autopep8 >= 1.4.0, < 1.5.0",
            "flake8 >= 3.7.0, < 3.8.0",
            "flake8-bugbear >= 19.3.0, < 20.0.0",
            "mock >= 3.0.5, < 4.0.0",
            "mypy >= 0.720, < 1.0.0",
            "pytest >= 4.0.0, < 5.0.0",
            "pytest-mock >= 1.10.4, < 1.11.2",
            "snakeviz >= 2.0.0, < 3.0.0",
            "tables >= 3.4.0, < 3.5.0",
            "xlrd >= 1.0.0, < 2.0.0",  # scripts/convert_dgcl_xlsx_to_csv.py
        ]
    },
    packages=find_packages(exclude=["tests*"]),
)
