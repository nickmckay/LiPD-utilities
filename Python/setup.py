from setuptools import setup, find_packages
from os import path
import os
import io
import sys
from distutils.command.install import install
from distutils.core import setup

here = path.abspath(path.dirname(__file__))
version = '0.2.8.8'


# Read the readme file contents into variable
if sys.argv[-1] == 'publish' or sys.argv[-1] == 'publishtest':
    os.system('pandoc README.md -f markdown -t rst -s -o README.txt')

readme_file = io.open('README.txt', encoding='utf-8')
# Fallback long_description in case errors with readme file.
# long_description = "Welcome to LiPD. Please reference the README file in the package for information"

with readme_file:
    long_description = readme_file.read()

# Publish the package to the live server

if sys.argv[-1] == 'publish':
    # Register the tarball, upload it, and trash the temp readme rst file
    os.system('python3 setup.py register')
    # os.system('python3 setup.py sdist upload')
    os.system('python3 setup.py sdist')
    os.system('twine upload dist/* --skip-existing')
    os.remove('README.txt')
    sys.exit()

# Publish the package to the test server
elif sys.argv[-1] == 'publishtest':
    # Create dist tarball, register it to test site, upload tarball, and remove temp readme file
    os.system('python3 setup.py sdist')
    os.system('python3 setup.py register -r https://test.pypi.org/legacy')
    os.system('twine upload -r test dist/LiPD-' + version + '.tar.gz')
    # Trash the temp rst readme file
    os.remove('README.txt')
    sys.exit()


# Do all the setup work
setup(
    name='LiPD',
    version=version,
    author='C. Heiser',
    author_email='heiser@nau.edu',
    packages=find_packages(),
    url='https://github.com/nickmckay/LiPD-utilities',
    license='GNU Public',
    description='LiPD utilities to process, convert, and analyze data.',
    # long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="paleo R matlab python paleoclimatology linkedearth",
    install_requires=[
        "bagit",
        "demjson3",
        "xlrd",
        "numpy",
        "pandas",
        "requests",
        "sip",
    ],
)
