import setuptools

setuptools.setup(
    name='deskapp',
	version = "0.0.3",
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://github.com/ruckusist/deskapp',
    packages=setuptools.find_packages(),
    description="An Open Source Terminal basesd Program Manager. Write and manage your own apps in this framework.",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    # long_description="THIS IS WORKING",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['termcolor', 'jinja2'],
    #########
    entry_points = {
        'console_scripts': ['deskapp=deskapp.cli:main']
    },
)
