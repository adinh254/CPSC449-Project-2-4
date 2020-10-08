from setuptools import setup


setup(
    name='CPSC449-Project2',
    version='1.0.1',
    author='Andrew Dinh',
    packages=['user_api','timeline_api'],
    include_package_data=True,
    install_requires=['Flask']
)
