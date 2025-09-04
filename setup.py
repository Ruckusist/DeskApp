from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).with_name('README.md').read_text(encoding='utf-8')

setup(
    name='Deskapp',
    version='0.1.0',
    description='An Open Source terminal-based app framework and server.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://ruckusist.com/deskapp',
    packages=find_packages(include=['deskapp*', 'sidedesk*']),
    include_package_data=True,
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
    python_requires='>=3.8',
    install_requires=[
        'passlib',
        'boto3',
        'tomli; python_version<"3.11"',
    ],
    entry_points={
        'console_scripts': [
            'deskapp=deskapp.__main__:main',
            'sidedesk=sidedesk.__main__:main',
            'deskchat=deskapp.deskchat.__main__:main',
            'deskapp-aws=deskapp.aws.__main__:main',
        ]
    },
)
