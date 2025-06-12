from setuptools import setup, find_packages

setup(
    name="ultra_modern_browser",
    version="4.0.0",
    description="Ultra-Modern Browser with VLESS VPN",
    author="Merimok",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pywebview>=3.6,<5.0",
        "PyQt5>=5.15.0",
        "pystray>=0.17.3",
        "Pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "isort", 
            "flake8", 
            "mypy",
            "pytest",
            "pytest-mock"
        ],
        "webui": [
            "beautifulsoup4>=4.9.0",  # For HTML parsing
        ],
        "monitoring": [
            "psutil>=5.8.0",          # For system monitoring
            "sentry-sdk>=1.0.0",      # For error reporting
        ],
        "automation": [
            "selenium>=4.0.0",        # For web automation
        ],
    },
    entry_points={
        "console_scripts": [
            "ultra-browser=ultra_modern_browser.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Framework :: Pytest",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
)
