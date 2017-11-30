from setuptools import setup, find_packages

# git+<url>@<branch>#egg=<package_name>-<tag>
setup(
    name='weather-serial',
    version='1.0',
    packages=find_packages(),
    install_requires=['pyserial', 'weather_server>=1.1'],
    dependency_links = [
        'git+https://github.com/ngunderson/weather_server.git@master#egg=weather_server-1.1'
    ]
)
