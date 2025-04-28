from setuptools import setup, find_packages

setup(
    name="noteapp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "motor",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "python-dotenv",
        "pytest",
        "pytest-asyncio",
        "httpx"
    ],
) 