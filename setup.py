from setuptools import setup

setup(
    name='checkannotations',
    version='0.1',
    description='Check for annotations',
    author='Tom Cammann',
    author_email='tom.cammann@hpe.com',
    packages=['checkannotations'],
    entry_points={
    'console_scripts': [
        'checka = checkannotations.checkannotations:main',
    ],
},
)
