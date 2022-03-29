import setuptools
from distutils.core import setup

setup(
    name='deskapp',
	version = "0.0.1",
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://github.com/ruckusist/deskapp',
    packages=setuptools.find_packages(),
    description="An Open Source Terminal basesd Program Manager. Write and manage your own apps in this framework.",
    long_description=open('README.txt').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    # install_requires=list(x.strip('\n') for x in open('requirements.txt', 'r').readlines()),
    install_requires=['termcolor', 'jinja2'],
    #########
    entry_points = {
        'console_scripts': ['deskapp=deskapp.cli:main']
    },
    ########
    # this did not work as expected and should not be doing this
    # right now.
    # 
    # include_package_data=True,
    # package_data = {
    #     '': ['deskapp/mods/templates/*.j2']
    # }
)
