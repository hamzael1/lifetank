from setuptools import setup

setup(
    name='lifetank-cli-client',
    version='1.0',
    author='Hamza El',
    url='https://github.com/hamzael1/lifetank',
    python_requires='>=3.6',
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        lifetank=main:cli
    '''
)