from setuptools import setup, find_packages

setup(
    name='dvarpal',
    version='0.0.3',
    url="https://github.com/sharmaak/dvarpal",
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
