import setuptools
from distutils.core import setup

setup(
    name='DeskApp',
    version='0.0.2',
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://github.com/ruckusist/deskapp',
    packages=setuptools.find_packages(),
    description="A terminal basesd program manager.",
    long_description=open('README.txt').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #########
    entry_points = {
        'console_scripts': ['deskapp=deskapp.cli:main']
    },
    ########
    include_package_data=True,
    package_data = {
        '': ['deskapp/mods/templates/*.j2']
    }
)
