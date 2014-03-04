from setuptools import setup, find_packages
import os,sys

version = '1.0'

if sys.version_info < (2, 5):
	    # Python 2.4 seems to have issues with setuptools collecting its
    # requirement packages from PyPI using HTTPS. This has been encountered
    # using Python 2.4.3/x86 on Windows 7/SP1/x64 with setuptools 0.7.2. As a
    # workaround we replace setuptools's PackageIndex class with one that
    # always uses the HTTP transfer protocol instead of HTTPS when dealing with
    # this Python version.
    #
    # Note that this workaround affects only setuptools's automated requirement
    # package downloading. Any requirement packages can still be installed
    # manually by the user, using a suitable package index source URL.
    import setuptools.package_index
    OriginalPackageIndex = setuptools.package_index.PackageIndex
    class NoHTTPSPackageIndex(OriginalPackageIndex):
        def __init__(self, *args, **kwargs):
            OriginalPackageIndex.__init__(self, *args, **kwargs)
            cue = "https:"
            if self.index_url.lower().startswith(cue):
	        self.index_url = "http:" + self.index_url[len(cue):]
    setuptools.package_index.PackageIndex = NoHTTPSPackageIndex

setup(name='secomba.migration',
      version=version,
      description="secom.ba.gov.br site content migration",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/rudaporto/secomba.migration.git',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['secomba', 'secomba.migration'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'MySQL-python',
	  'zope.sqlalchemy==0.6.1',
	  'sqlalchemy<0.7-dev',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
