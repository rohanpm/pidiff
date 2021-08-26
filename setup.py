from setuptools import setup, find_packages


def get_description():
    return "The Python interface diff tool"


def get_long_description():
    text = open("README.md").read()

    # The README starts with the same text as "description",
    # which makes sense, but on PyPI causes same text to be
    # displayed twice.  So let's strip that.
    return text.replace(get_description() + ".\n\n", "", 1)


def get_install_requires():
    return open("requirements.txt").readlines()


setup(
    name="pidiff",
    version="1.7.0",
    author="Rohan McGovern",
    author_email="rohan@mcgovern.id.au",
    url="https://github.com/rohanpm/pidiff",
    packages=find_packages(exclude=["tests", "tests.*"]),
    license="GNU General Public License",
    description=get_description(),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    install_requires=get_install_requires(),
    python_requires='>=3.8',
    entry_points={"console_scripts": ["pidiff=pidiff._impl.command:main"]},
    project_urls={
        "Documentation": "https://pidiff.dev/",
        "Changelog": "https://github.com/rohanpm/pidiff/blob/master/CHANGELOG.md",
    },
)
