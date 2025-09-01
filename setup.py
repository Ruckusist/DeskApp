# Modern Setup.py using setuptools
# Updated to use setuptools instead of deprecated distutils
# last updated by code review

from setuptools import setup, find_packages

setup(
    name='Deskapp',
    version="0.1.0",
    description='An Open Source Terminal-based Program Manager. Write and manage your own apps in this framework.',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://ruckusist.com/deskapp',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business',
    ],
    python_requires='>=3.7',
    install_requires=[
        'rich',
        'passlib',
    ],
    entry_points={
        'console_scripts': ['deskapp=deskapp.__main__:main']
    },
)