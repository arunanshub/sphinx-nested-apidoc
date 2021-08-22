from setuptools import find_packages, setup

setup(
    name="sphinx-nested-apidoc",
    version="0.3.2",
    author="Arunanshu Biswas",
    author_email="mydellpc07@gmail.com",
    description="sphinx-nested-apidoc: When flattened is not enough",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    entry_points=dict(
        console_scripts=[
            "sphinx-nested-apidoc=sphinx_nested_apidoc.__main__:main"
        ],
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Documentation :: Sphinx",
    ],
    install_requires=["sphinx"],
    url="https://github.com/arunanshub/sphinx-nested-apidoc",
)
