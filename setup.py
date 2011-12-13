try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

kwargs = {}

version = "1.0.0"

setup(
    name="httpshell",
    version=version,
    packages=["httpshell"],
    install_requires=['pygments'],
    py_modules=['ez_setup'],
    scripts=['httpsh'],
    author="Chris Longo",
    author_email="chris.longo@gmail.com",
    url="https://github.com/chrislongo/HttpShell/",
    download_url="http://github.com/downloads/chrislongo/HttpShell/httpshell-%s.tar.gz" % version,
    license="TBD",
    description="TODO",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Networking'
          ]
    )
