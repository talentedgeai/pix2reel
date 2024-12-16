from setuptools import setup, find_packages

setup(
    name="pix2reel",               # Name of your library
    version="0.1.0",                 # Library version
    author="Khang Nguyen",              # Your name or organization
    author_email="khang.nguyen@talentedge.ai",  # Your email
    description="A library to generate reels from images",  # Short description
    long_description=open("README.md").read(),  # Detailed description (from README)
    long_description_content_type="text/markdown",  # Content type for long description
    url="https://github.com/username/my_library",  # URL of your library
    packages=find_packages(),        # Automatically find all packages in the library
    install_requires=[               # Dependencies required for installation
        "openai==1.57.1",
        "requests>=2.25.1"
    ],
    classifiers=[                    # Metadata for PyPI and others
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",         # Minimum Python version required
)
