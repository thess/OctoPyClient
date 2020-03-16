import re
import os
from setuptools import setup

INSTALL_REQUIRES = [
    "PyGObject",
    "pycairo",
    "humanize",
    "attrs",
    "sdnotify",
    "requests",
    "urllib3"
]

EXTRAS_REQUIRE = {}

version = re.search('^__version__\s*=\s*"(.*)"',
    open('octopyclient/octopyclient.py').read(), re.M).group(1)


setup(
    name="OctoPyClient", version=version,
    packages=['octopyclient', 'octopyclient/octorest', 'octopyclient/panels'],
    package_data={ 'octopyclient': ["styles/*", "styles/images/*"]},
    install_requires=INSTALL_REQUIRES, extras_require=EXTRAS_REQUIRE,
    author="Ted Hess", author_email="thess@kitschensync.net", license="LICENSE",
    url="https://github.com/thess/OctoPyClient", description="OctoPrint touchscreen client",
    entry_points={ "console_scripts": ['octopyclient = octopyclient.octopyclient:main'] }
    )

