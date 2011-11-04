from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.listmaker',
      version=version,
      description="A formlib widget for when users need to add items to a list",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'
        ],
      keywords='formlib widget list table grid data',
      author='Danilo G. Botelho',
      author_email='danilogbotelho@yahoo.com',
      url='',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.formlib',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
