from setuptools import setup
import os

version_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION'))

setup(
    name='sybillian',
    version=version_file.read().strip(),
    py_modules=['credentials', 'responder', 'sybil', 'populator', 'database'],
    include_package_data=True,
    install_requires=[
        'botornot',
        'tweepy',
        'sqlalchemy'
    ],
    entry_points='''
        [console_scripts]
        sybillian=responder:runtime
    ''',
)