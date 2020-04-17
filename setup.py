from setuptools import setup, find_packages

setup(
    name="ibm_service_validator",
    version="0.0.1",
    description="Python package, Schemathesis, extended to include IBM API Handbook validation.",
    url="https://github.ibm.com/CloudEngineering/ibm-service-validator",
    author="Barrett Schonefeld, IBM",
    author_email="barrett.schonefeld@ibm.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["click", "schemathesis"],
    entry_points="""
        [console_scripts]
        ibm-service-validator=ibm_service_validator.cli.run_schemathesis:run_schemathesis
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
