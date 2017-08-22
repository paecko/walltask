from setuptools import setup

setup(
    name="walltask",
    version='0.1',
    py_modules=['walltask'],
    entry_points='''
        [console_scripts]
        walltask=walltask:cli
    ''',
)