from setuptools import setup, find_packages

setup(
    name='volta-gen',
    version='1.0.0',
    packages=find_packages(),
    requires=['lark'],
    install_requires=['lark'],
    author='kaazedev',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/volta-dev/gen',
    },
    entry_points={
        'console_scripts': [
            'volta-gen=src.main:main',
        ],
    },
)