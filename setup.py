# This is the old implementation.
# deprecated in v. 0.0.4. 
# 7-26-22.
"""
import setuptools

setuptools.setup(
    name='deskapp',
	version = "0.0.4",
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://github.com/ruckusist/deskapp',
    packages=setuptools.find_packages(),
    description="An Open Source Terminal basesd Program Manager. Write and manage your own apps in this framework.",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['jinja2'],
    #########
    entry_points = {
        'console_scripts': ['deskapp=deskapp.cli:main']
    },
)
"""

# New Version of Setup.py
# now using distutils.
# last updated 7-26-22.


from distutils.core import setup

setup(
    name='Deskapp',
    version='0.0.4',
    description='An Open Source Terminal basesd Program Manager. Write and manage your own apps in this framework.',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://ruckusist.com/deskapp',
    packages=['deskapp'],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Office/Business',
          ],
    install_requires=['jinja2'],
    entry_points = {
        'console_scripts': ['deskapp=deskapp.cli:main']
    },
)