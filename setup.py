from setuptools import find_packages, setup


setup(
    name='roombai7',
    version='1.0',
    license='MIT',
    description='Python program and library to control iRobot Roomba i7 ' \
                'Vacuum Cleaner',
    author_email='alexander@landmesser.online',
    url='https://github.com/Alex-Ala/roombai7',
    packages=find_packages(),
    install_requires=['paho-mqtt', 'pillow'],
    include_package_data=True,
    entry_points={
    }
)
