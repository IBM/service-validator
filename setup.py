from setuptools import setup

setup(
    name='schemathesis-ibm',
    version='0.1',
    description='Python package, Schemathesis, extended to include IBM API Handbook validation.',
    url='https://github.ibm.com/CloudEngineering/schemathesis-endpoint-validator',
    author='IBM',
    author_email='barrett.schonefeld@ibm.com',
    packages=['schemathesis-ibm'],
    install_requires=[
        'schemathesis',
    ],
    zip_safe=False
)
