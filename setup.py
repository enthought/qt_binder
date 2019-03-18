from setuptools import setup, find_packages


long_description = """\
QtBinder provides a way to bind Qt widgets to Traits models.
"""

setup(
    name='qt_binder',
    version='0.2.1',
    author='Enthought, Inc.',
    author_email='info@enthought.com',
    description='Traits bindings for Qt',
    long_description=long_description,
    url='https://github.com/enthought/qt_binder',
    license="BSD",
    packages=find_packages(exclude=['examples', 'examples.*']),
    package_data={
        'qt_binder.tests': ['*.ui'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    use_2to3=False,
    install_requires=[
        'six',
        'traits',
        'pyface',
        'traitsui',
    ],
)
