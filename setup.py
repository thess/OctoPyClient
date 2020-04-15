import sys
import os
import re
from setuptools import setup

# Python 3.6+ required
PYTHON_MINVER = (3, 6)
if sys.version_info < PYTHON_MINVER:
    sys.exit("Python %s.%s or later is required.\n" % PYTHON_MINVER)

INSTALL_REQUIRES = [
    "PyGObject",
    "pycairo",
    "humanize",
    "attrs",
    "psutil",
    "sdnotify",
    "requests",
    "urllib3",
    "pyyaml"
]

# Notes to self (IMMV):
# [Optional] Install build tools
#    $ sudo apt install git build-essential pkg-config
# X11 requirements if console only system installed. Ex: Raspbian Lite
#    $ sudo apt install xorg
# [Hardware/vendor specific] Install/configure display drivers and setup for X11
# Install the necessary Python3 environment and GTK+3 dependencies
# General python3 installation requirements
#    $ sudo apt install python3-pip python3-dev python3-setuptools python3-virtualenv virtualenv
# Install system PyGObject, pycairo, pyyaml
#    $ sudo apt install python3-yaml python3-gi python3-gi-cairo gir1.2-gtk-3.0
# Create and enter virtual environment
#    $ virtualenv --python=python3 --system-site-packages venv
#    $ source venv/bin/activate
#    $ pip install pip --upgrade
#    $ pip install --no-cache-dir octopyclient
# [testing repo]
#    $ pip install --index-url https://test.pypi.org/simple/ --no-cache-dir --no-deps octopyclient

EXTRAS_REQUIRE = {}

version = re.search('^__version__\\s*=\\s*"(.*)"',
                    open('octopyclient/octopyclient.py').read(), re.M).group(1)

if 'DEBIAN_DESCRIPTION' in os.environ:
    readmeDoc = os.environ['DEBIAN_DESCRIPTION']
else:
    readmeDoc = "README.md"

with open(readmeDoc, "r") as fh:
    readme = fh.read()

setup(
    name="OctoPyClient", version=version,
    packages=['octopyclient', 'octopyclient/octorest', 'octopyclient/panels'],
    package_data={'octopyclient': ["styles/*", "styles/images/*"]},
    install_requires=INSTALL_REQUIRES, extras_require=EXTRAS_REQUIRE,
    author="Ted Hess", author_email="thess@kitschensync.net", license="LICENSE",
    maintainer="Ted Hess", maintainer_email="thess@kitschensync.net",
    url="https://github.com/thess/OctoPyClient",
    description="OctoPyClient - A touchscreen client for OctoPrint",
    long_description=readme,
    long_description_content_type="text/markdown",
    entry_points={'console_scripts': ['octopyclient = octopyclient.octopyclient:main']},
    classifiers=[

        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
    )
