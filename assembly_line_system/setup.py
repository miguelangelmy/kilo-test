from setuptools import setup, find_packages

setup(
    name="assembly_line_system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spade==4.1.0",
        "ray[rllib]>=2.35.0,<2.48.0",
        "gymnasium==0.28.1",
        "numpy>=1.24.0",
        "tensorflow>=2.12.0",
        "torch>=2.0.1"
    ],
    extras_require={
        "dev": [
            "pytest==7.4.0",
            "pytest-bdd==6.1.1",
            "pre-commit==3.2.2",
            "black==23.7.0",
            "isort==5.12.0"
        ],
        "docs": [
            "mkdocs==1.4.3",
            "mkdocs-material==9.1.7"
        ]
    },
    entry_points={
        "console_scripts": [
            "assembly_line_sim=assembly_line_system.simulation:main",
        ],
    },
)