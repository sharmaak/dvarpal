from setuptools import setup, find_packages

setup(
    name='dvarpal',
    version='0.0.1-beta',
    packages=find_packages(),
    install_requires=[
        'PyYAML'
        'requests'
        'pyotp'
        'upstox-python-sdk'
        'undetected_chromedriver'
    ],
    # Include additional metadata like author, author_email, description, etc.
)
