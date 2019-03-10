from setuptools import setup, find_packages


def get_description():
    return 'Python interface diff'


def get_long_description():
    text = open('README.md').read()

    # The README starts with the same text as "description",
    # which makes sense, but on PyPI causes same text to be
    # displayed twice.  So let's strip that.
    return text.replace(get_description() + '.\n\n', '', 1)


def get_install_requires():
    return open('requirements.txt').readlines()


setup(
    name='pidiff',
    version='0.2.0',
    author='Rohan McGovern',
    author_email='rohan@mcgovern.id.au',
    url='https://github.com/rohanpm/pidiff',
    packages=find_packages(exclude=['tests', 'tests.*']),
    license='GNU General Public License',
    description=get_description(),
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    install_requires=get_install_requires(),
    entry_points={
        'console_scripts': [
            'pidiff=pidiff._command:main',
        ]
    }
)
