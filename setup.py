import os
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="prompt-security-fuzzer",
    version=os.getenv('PKG_VERSION', '0.0.1'),
    author="Prompt Security",
    author_email="support@prompt.security",
    description="LLM and System Prompt vulnerability scanner tool",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/prompt-security/ps-fuzz",
    packages=find_packages(),
    package_data={
        'ps_fuzz': ['attack_data/*'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    python_requires='>=3.10',
    install_requires=[
        "httpx>=0.27.0,<1.0.0",
        "openai>=2.45.0,<4.0.0",
        "langchain>=1.3.9,<2.0.0",
        "langchain-community>=0.4.2,<0.5.0",
        "langchain-core>=1.5.4,<2.0.0",
        "langchain-openai>=1.5.1,<2.0.0",
        "langchain-ollama>=1.1.0,<2.0.0",
        "argparse==1.4.0",
        "python-dotenv>=1.2.2,<2.0.0",
        "tqdm>=4.66.3",
        "colorama==0.4.6",
        "prettytable==3.10.0",
        "pandas==2.2.3",
        "inquirer==3.2.4",
        "prompt-toolkit==3.0.43",
        "fastparquet==2024.11.0",
        "chromadb>=1.3.5,<2.0.0",
        "langchain-chroma>=1.1.0,<2.0.0",
        "tiktoken>=0.11.0"
    ],
    extras_require={
        "dev": ["pytest==7.4.4"]
    },
    entry_points={
        'console_scripts': [
            'prompt-security-fuzzer=ps_fuzz.cli:main',
        ],
    },
    license="MIT",
)
