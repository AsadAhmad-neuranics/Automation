from setuptools import setup, find_packages

setup(
    name='scpi-framework',
    version='0.2.0',
    author='Asad Ahmad',
    author_email='asad@neuranics.com',
    description='A framework for SCPI communication with instruments',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
    'numpy',
    'matplotlib',
    'pyvisa',
    'pytest',
    'scipy',

    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: SOON :: SOON',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)