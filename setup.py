from setuptools import setup, find_packages

setup(
    name='necrodancer-pbr',
    version='0.1',
    description='Pre-Built Racing mod generator for Crypt of the NecroDancer',
    url='https://github.com/ashastral/necrodancer-pbr',
    author='ashastral',
    packages=['pbr'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pbr-cli=pbr_cli:main'
        ]
    }
)
