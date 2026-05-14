from setuptools import setup, find_packages

setup(
    name="tax-form-agent",
    version="1.0.0",
    description="AI agent for explaining German tax registration form 'Fragebogen zur steuerlichen Erfassung (Einzelunternehmen)'",
    author="Ekaterina Marova",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "tax_form_agent": ["../data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "tax-form-agent=tax_form_agent.cli:main",
        ],
    },
    install_requires=[],  # no external dependencies
)