#!/usr/bin/env python

from distutils.core import setup

setup(name='Simple File Server',
      version='1.0',
      description='Allows transfering files using a http server',
      author='Saevon Kyomae',
      author_email='saevon.kyomae@gmail.com',
      url='',
      packages=[],
      py_modules=['file_server'],
      scripts=['file_server.py'],
     )
