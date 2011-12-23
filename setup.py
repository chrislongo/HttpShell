import sys
from httpshell import version

try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

REQUIRES = ["pygments>=1.1.1", "httplib2>=0.7.0", "oauth2>=1.5"]

if sys.version_info <= (2, 7):
    REQUIRES.append("argparse>=1.2.1")


setup(
    name="httpshell",
    version=version.VERSION,
    packages=["httpshell"],
    install_requires=REQUIRES,
    py_modules=["ez_setup"],
    scripts=["httpsh"],
    author="Chris Longo",
    author_email="chris.longo@gmail.com",
    url="https://github.com/chrislongo/HttpShell/",
    download_url="http://github.com/downloads/chrislongo/HttpShell/httpshell-%s.tar.gz" % version.VERSION,
    description="An interactive shell for issuing HTTP commands to a web server or REST API",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: System :: Networking"
          ]
    )
