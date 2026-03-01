from setuptools import setup

setup(
    name='lunarlander-cli',
    version='1.0.0',
    description='Terminal client for Lunar Lander game',
    author='Carl Fugate',
    author_email='carl@example.com',
    packages=['cli'],
    install_requires=[
        'rich>=13.0.0',
        'blessed>=1.20.0',
        'keyboard>=0.13.5',
        'websockets>=12.0',
        'aiohttp>=3.9.0'
    ],
    entry_points={
        'console_scripts': [
            'lunarlander-cli=terminal_client:main'
        ]
    },
    python_requires='>=3.8'
)