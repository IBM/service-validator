from setuptools import setup, find_packages

__version__ = "0.4.2"

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="ibm_service_validator",
    version=__version__,
    description="Python package, Schemathesis, extended to include IBM API Handbook validation.",
    url="https://github.com/IBM/service-validator",
    author_email="devexdev@us.ibm.com",
    license="Apache 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["click", "ibm-cloud-sdk-core", "pyyaml", "schemathesis"],
    entry_points="""
        [console_scripts]
        ibm-service-validator=ibm_service_validator.cli:ibm_service_validator
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
