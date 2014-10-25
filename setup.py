'''
Setuptools configuration
'''

from setuptools import setup, find_packages

setup(
    name="fakelargefile",
    version="0.0.1",
    author="Lauritz Thaulow",
    author_email="lauritz.thaulow@gmail.com",
    description="Simulate and alter a very large file.",
    license="GPLv3",
    packages=['fakelargefile', 'tests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    include_package_data=True,
)
