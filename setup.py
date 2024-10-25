from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name="lunchbot-cli",
    version="1.0",
    packages=find_packages(),
    install_requires=required_packages, 
    entry_points={
        'console_scripts': [
            'lunchbot=lunchbot.lounasbotti:main', 
        ],
    },
    python_requires='>=3.6',  
    include_package_data=True,  
    description="A CLI tool for fetching lunch menus and weather information.",
    author="Jerry Shadbolt",  
    author_email="jerry.shadbolt@windowslive.com",  
    license="MIT",  
    url="https://github.com/jerryshadb/lunchbot",  
)
