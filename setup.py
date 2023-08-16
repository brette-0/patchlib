from setuptools import setup

setup(
    name="get_patchlib",
    #packages=["patchlib"],
    package_dir={"": "src"},
    version="1.1",
    description="Patch file handler",
    author="Brette",
    keywords="Patch file handler",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BrettefromNesUniverse/patchlib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
    extras_require={
    "docs": [
        "sphinx",
        ]
    }
)