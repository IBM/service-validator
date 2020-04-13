from setuptools import setup

setup(
    name="schemathesis-ibm",
    version="0.1",
    description="Python package, Schemathesis, extended to include IBM API Handbook validation.",
    url="https://github.ibm.com/CloudEngineering/schemathesis-endpoint-validator",
    author="Barrett Schonefeld, IBM",
    author_email="barrett.schonefeld@ibm.com",
    packages=["src"],
    install_requires=["click", "schemathesis"],
    entry_points="""
        [console_scripts]
        schemathesis-ibm=src.cli.run_schemathesis:run_schemathesis
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
