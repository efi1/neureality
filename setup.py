from setuptools import find_packages, setup

def parse_requirements(filename)-> list:
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line and not line.startswith("#")]

setup(
    name='NeuRealityProject',
    version='0.1.0',
    description='NeuReality task assignment',
    packages=find_packages(where="."),  # searches from current directory
    package_dir={"": "."},              # maps root to actual package structure
    package_data={
        "tests.cfg.cfg_global": ["*.json"],
        "tests.cfg.cfg_parameterized_tests": ["*.json"],
        "tests.cfg.cfg_non_parameterized_tests": ["*.json"]
    },

    # metadata
    author='',
    author_email='',
    license='proprietary',
    install_requires=parse_requirements('requirements.txt'),
)