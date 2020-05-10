#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='whirling',
    version='0.0.3',
    description='Audio visualizer using advanced audio feature extraction',
    url='https://github.com/nate-h/Whirling',
    classifiers=[
        'Programming Language :: Python :: 3.6.8',
    ],
    package_dir={'': '.'},
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pygame',
        'python-vlc',
        'rx',
        'sklearn',
        'librosa',
        'coloredlogs',
        'jupyter',
        'matplotlib',
        'PyOpenGL',
        'spleeter',
        'schema'
    ],
    entry_points={
        'console_scripts': [
            'run_whirling=whirling.run_whirling:main',
            'run_cache_tracks=whirling.run_cache_tracks:main',
        ],
    },
    scripts=[
    ],
)