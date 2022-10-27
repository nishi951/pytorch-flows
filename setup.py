#!/usr/bin/env python3

from distutils.core import setup

setup(name='pytorch-flow',
      version='0.2.0',
      description='a simple flow with multiple experiments',
      author='Mark Nishimura',
      author_email='nishimuramarky@yahoo.com',
      package_dir={'': 'src'},
      packages=[
          'flow_utils',
          'config_utils',
      ],
      scripts=[
          'src/flow_utils/flow_create'
      ]
)
