#!/usr/bin/env python3

from distutils.core import setup

setup(name='pytorch-flow',
      version='0.0.1',
      description='a simple flow with multiple experiments',
      author='Mark Nishimura',
      author_email='nishimuramarky@yahoo.com',
      packages=[
          'core',
          'experiments',
      ],
)
