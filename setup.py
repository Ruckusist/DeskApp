import setuptools
from distutils.core import setup

setup(
    name='DeskApp',
    version='0.0.1',
    author='Ruckusist',
    author_email='ruckusist@alphagriffin.com',
    url='https://github.com/ruckusist/deskapp',
    packages=setuptools.find_packages(),
    description="A terminal basesd program manager.",
    long_description=open('README.txt').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
