from setuptools import setup, find_packages

setup(
    name="merchant-bi-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "prometheus-client>=0.12.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "aioredis>=2.0.0",
        "motor>=2.5.0",
        "aiormq>=6.4.2",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="商户智能经营分析平台共享库",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
    ],
) 