from setuptools import setup, find_packages

setup(
    name='scpi-framework',
    version='0.1.0',
    author='Asad Ahmad',
    author_email='asad@neuranics.com',
    description='A framework for SCPI communication with instruments',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List your project dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)