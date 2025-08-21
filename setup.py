from setuptools import find_packages, setup

def parse_requirements(filename) -> list:
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line and not line.startswith("#")]

setup(
    name='NeuRealityProject',
    version='0.1.0',
    description='NeuReality task assignment',
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    package_data={
        "tests.cfg.cfg_global": ["*.json"],
        "tests.cfg.cfg_parameterized_tests": ["*.json"],
        "tests.cfg.cfg_non_parameterized_tests": ["*.json"]
    },
    author='',
    author_email='',
    license='proprietary',
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)