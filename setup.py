#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='whirling',
    version='0.1.0',
    description='Audio visualizer using track segmentation and audio feature extraction',
    url='https://github.com/nate-h/Whirling',
    classifiers=[
        'Programming Language :: Python :: 3.6.9',
    ],
    package_dir={'': '.'},
    packages=find_packages(),
    install_requires=[
        'numpy==1.18.5',
        'pygame',
        'python-vlc',
        'Rx==3.2.0',
        'sklearn',
        'librosa==0.8.0',
        'coloredlogs',
        'jupyter',
        'matplotlib',
        'PyOpenGL==3.1.5',
        'spleeter==2.2.2',
        'schema==0.7.4'
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
