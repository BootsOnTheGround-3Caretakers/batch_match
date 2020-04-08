from setuptools import setup, find_packages

__version__ = "0.1"

setup(
    name="voluntarily",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "flask",
        "flask-restful",
        "flask-jwt-extended",
        "flask-marshmallow",
        "elasticsearch",
        "python-dotenv",
        "passlib",
        "apispec[yaml]",
        "apispec-webframeworks",
    ],
    entry_points={
        "console_scripts": [
            "voluntarily = voluntarily.manage:cli"
        ]
    },
)
