from setuptools import setup, find_packages

setup(
    name='mltrace',
    version='0.1',
    description='Lineage and tracing for ML pipelines',
    author='shreyashankar',
    author_email='shreya@cs.stanford.edu',
    # license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'gitpython',
        'numpy',
        'pandas',
        'psycopg2-binary',
        'pytest',
        'sklearn',
        'sqlalchemy'
    ]
)
