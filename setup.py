from setuptools import setup, find_packages

import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="mltrace",
    version="0.14",
    description="Lineage and tracing for ML pipelines",
    long_description=README,
    long_description_content_type="text/markdown",
    author="shreyashankar",
    author_email="shreya@cs.stanford.edu",
    license="Apache License 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Bug Tracking",
    ],
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "click",
        "docker",
        "flask",
        "furo",
        "gitpython",
        "psycopg2-binary",
        "pytest",
        "python-dotenv",
        "sqlalchemy",
    ],
    entry_points="""
        [console_scripts]
        mltrace=mltrace.cli.cli:mltrace
    """,
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/loglabs/mltrace/issues",
        "Source Code": "https://github.com/loglabs/mltrace",
    },
)
