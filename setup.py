from setuptools import setup

about = {}
with open("configure_with_sudo/__about__.py") as fp:
    exec(fp.read(), about)

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zachary Cutlip",
    author_email="uid000@gmail.com",
    url="https://github.com/zcutlip/configure-with-sudo",
    license="MIT",
    packages=["configure_with_sudo"],
    python_requires=">=2.7",
    install_requires=[],
    package_data={"configure_with_sudo": ["config/*"]},
)
