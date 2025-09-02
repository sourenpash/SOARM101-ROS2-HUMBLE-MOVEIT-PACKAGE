from setuptools import setup

package_name = 'soarm101_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'lerobot', 'draccus', 'rerun'],
    zip_safe=True,
    maintainer='',
    maintainer_email='',
    description='SOARM101 bridge for MoveIt',
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'soarm101_controller = soarm101_control.soarm101_controller:main',
        ],
    },
    python_requires='>=3.10',
)
