python-package-template <a href="https://sarahcgallLtd.github.io/r-package-template/"><img src="man/figures/logo.png" align="right" height="138" alt="" /></a>

[//]: # (======================================= UNCOMMENT BELOW ======================================================)

[//]: # (================)

[//]: # (<!-- badges: start -->)

[//]: # (<!-- [![Release]&#40;https://img.shields.io/badge/Release-development%20version%200.0.1-blue&#41;]&#40;https://github.com/sarahcgallLtd/python-package-template/blob/main/CHANGELOG.md&#41; -->)

[//]: # (<!-- [![CI]&#40;https://github.com/sarahcgallLtd/python-package-template/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/sarahcgallLtd/python-package-template/actions/workflows/ci.yml&#41; -->)

[//]: # (<!-- [![codecov]&#40;https://codecov.io/gh/sarahcgallLtd/python-package-template/graph/badge.svg?token=YOUR_TOKEN&#41;]&#40;https://codecov.io/gh/sarahcgallLtd/python-package-template&#41; -->)

[//]: # ()
[//]: # (<!-- badges: end -->)

[//]: # (## Overview)

[//]: # ()
[//]: # (`scgElectionsAU` is an R package providing comprehensive data and tools for analysing Australia’s federal election )

[//]: # (results from 2001 to 2022. It offers a unique insight into the dynamics of the electoral process in Australia, )

[//]: # (presented through a variety of datasets and functions.)

[//]: # ()
[//]: # (#### Datasets Included:)

[//]: # ()
[//]: # (* [`X`]&#40;https://sarahcgallLtd.github.io/scgElectionsAU/reference/summary.html&#41;: Data description.)

[//]: # ()
[//]: # (## Installation)

[//]: # ()
[//]: # (To install the development version of `scgElectionsAU`, use:)

[//]: # ()
[//]: # (``` r)

[//]: # (# Install the development version from GitHub)

[//]: # (devtools::install_github&#40;"sarahcgall/scgElectionsAU"&#41;)

[//]: # (```)

[//]: # ()
[//]: # (## Usage)

[//]: # (`scgElectionsAU` includes several helper functions to enhance data analysis:)

[//]: # ()
[//]: # ()
[//]: # (Example usage:)

[//]: # (``` r)

[//]: # (library&#40;scgElectionsAU&#41;)

[//]: # ()
[//]: # (# Load a dataset)

[//]: # (df <- scgUtils::get_data&#40;"majority"&#41;)

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (Explore detailed examples and dataset descriptions in the )

[//]: # ([package documentation]&#40;https://sarahcgallLtd.github.io/scgElectionsAU/reference/index.html&#41;.)

[//]: # ()
[//]: # (## Data Sources and Disclaimer)

[//]: # (#### Data Sources)

[//]: # (The datasets in the `scgElectionsAU` package are meticulously curated from the official results sourced from the [Australian Electoral Commission]&#40;https://www.aec.gov.au/&#41;.)

[//]: # (These datasets offer a comprehensive view of Australia's electoral outcomes and are crucial for in-depth analysis and research in political science, electoral studies, and related fields.)

[//]: # ()
[//]: # (#### Disclaimer)

[//]: # (While the utmost care has been taken to ensure the accuracy and reliability of the data, the Australian Electoral Commission )

[//]: # (was not involved in the development of this package and thus does not bear responsibility for any errors or omissions in the datasets. )

[//]: # (Users of `scgElectionsAU` should note that the package's creators have independently compiled, processed, and presented the data. )

[//]: # (Any discrepancies or inaccuracies found within the datasets do not reflect on the official records maintained by the Electoral Commission.)

[//]: # ()
[//]: # (#### Currency of Data)

[//]: # (The data included in this package are up-to-date as of 2 March 2025. Users should be aware that subsequent electoral )

[//]: # (events or data revisions by the Electoral Commission after this date may not be reflected in the current version of `scgElectionsAU`.)

[//]: # ()
[//]: # (## Future Additions and Updates)

[//]: # (Planned future additions include by-election and referendum results and enhanced datasets like `results_by_booths`. )

[//]: # (Upcoming functional updates will focus on visualising election results specific to Australia and making boundary)

[//]: # (adjustments for better comparative analysis.)

[//]: # ()
[//]: # (## Feedback and Contributions)

[//]: # (Suggestions and contributions are welcome. For any proposed additions, amendments, or feedback, please [create an issue]&#40;https://github.com/sarahcgallLtd/scgElectionsAU/issues&#41;.)

[//]: # ()
[//]: # (## Related Packages)

[//]: # (Check out [`scgUtils`]&#40;https://sarahcgallLtd.github.io/scgUtils&#41; for additional functions and visualisation tools.)

[//]: # (======================================== DELETE BELOW ========================================================)

# Python Package Template

This template is for developing a Python package.
For a useful resource, go to [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/), 
the [Python Packaging User Guide](https://packaging.python.org/en/latest/), or the 
[Hitchhikers Guide to Packaging](https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/).

## Create package
First, check that the name you want to call your package is available on PyPI.
Packages typically use kebab-case (e.g., scg-utils, scg-elections-au).
You can check availability via the command line:

```bash
pip search your-package-name
```

Or visit [PyPI](https://pypi.org/) and search.

From here, create a new repository with the name of your new package on GitHub.
To do this:

1. Select 'New' (green button)
2. Enter the new repository name (e.g., python-package-template)
3. Make either 'Public' or 'Private' (depending on whether you want it to be open source or private - client code)
4. Select 'Create repository'

Then, in your IDE (e.g., PyCharm, VS Code):

1. Open a terminal (Git Bash):
```bash
git init
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/sarahcgallLtd/your-package-name.git
git push -u origin main
```

This will connect your new package to GitHub.

## Clone the template from GitHub
Clone it into the new package root folder. This can be done in your IDE or by
following the below steps in a terminal.

```bash
# clone project from template repository
git clone https://github.com/sarahcgallLtd/python-package-template.git
```

If you want the contents of the cloned folder to be moved into the root directory,
do the following in your terminal.
```bash
# move into the cloned repository folder
cd python-package-template

# Remove the .git history
rm -rf .git

# Move everything up one directory level
mv * .[^.]* ..  # This moves files, including hidden ones

# Go back to the root directory
cd ..

# Remove the now empty directory
rmdir python-package-template
```


## Configure package
**Initial configurations**

- `pyproject.toml` - change package name, authors, description, and add details
- `NEWS.md` or `CHANGELOG.md` - update to fit description of new package (optional, but good practice)
- `README.md` - customise the overview, installation, usage, etc.; delete template sections as needed
- `src/your_package/logo.png` - replace with new logo if using for docs (create in Adobe Illustrator or similar)
- `src/your_package` - rename `src/package_name` to `src/my_package` (replace `my_package` with your package name).
  - `__init__.py` - update version and imports 
  - `example.py` - delete or rename
- tests/test_example.py - change package name and delete/rename as needed
- Add your license file if not MIT (update pyproject.toml accordingly)

**Package structure**

```
python-package-template/              # Root of the package
│
├── .github/                          # GitHub Actions settings            
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md             # Template for bug reports
│   │   └── feature_request.md        # Template for feature requests
│   └── workflows/
│       ├── ci.yml                    # Configuration for CI (tests, linting)
│       └── test-coverage.yml         # Configuration for code coverage with Codecov
│      
├── docs/                             # Documentation with Sphinx
│   ├── conf.py                       # Sphinx configuration
│   ├── index.rst                     # Main index for docs
│   └── _static/                      # Static files for docs
│       └── logo.png                  # Package logo (optional)
│                 
├── src/                              # Source code
│   └── your_package/                 # Replace 'your_package' with your package name
│       ├── __init__.py               # Package initializer
│       └── example.py                # Example module [DELETE ME]
│                   
├── tests/                            # Unit tests location 
│   ├── __init__.py                   # Test package initializer
│   └── test_example.py               # Example tests [DELETE ME]
│                 
├── .gitignore                        # Files/folders to ignore in Git               
├── .pre-commit-config.yaml           # Optional: Pre-commit hooks for linting/formatting
├── codecov.yml                       # Codecov configuration
├── CHANGELOG.md                      # Changelog for releases (optional)
├── LICENSE                           # License file (e.g., MIT)
├── MANIFEST.in                       # For including non-Python files in builds (if needed)
├── NEWS.md                           # News/updates (optional, can merge with CHANGELOG)
├── pyproject.toml                    # Project metadata, dependencies, build config
├── README.md                         # GitHub README
└── setup.cfg                         # Additional config if needed (Poetry handles most)
```

**Commands to use**

Install Poetry if not already: pip install poetry (or use their installer script).

```bash
# 1. Initialise or update dependencies
poetry install  # Installs deps and creates virtual env

# e.g., add a new dependency
poetry add some-package

# e.g., add a dev dependency (e.g., for testing)
poetry add --group dev pytest

# 2. Add a new module
# Manually create files in src/your_package/, e.g., touch src/your_package/new_module.py

# 3. Run tests
poetry run pytest

# 4. Build the package
poetry build

# 5. Check formatting/linting (if black and flake8 are installed)
poetry run black --check src/
poetry run flake8 src/

# 6. Bump version
# Edit pyproject.toml version, or use poetry version patch/minor/major

# 7. Publish to PyPI (after setting up API token)
poetry publish
```

**Create website**

Create a documentation website using Sphinx. Run the below once to set up.

```bash
# Install Sphinx as dev dep
poetry add --group dev sphinx sphinx-rtd-theme

# Initialize Sphinx (run in root, it will create docs/)
sphinx-quickstart docs

# Then build
cd docs
make html
```

Configure details in docs/conf.py (e.g., add extensions for autodoc).

For GitHub Pages deployment, add a workflow or use sphinx gh-deploy.

See Sphinx docs for more.

**Set up Code Coverage with Codecov**

1. Sign up at [codecov.io](https://app.codecov.io/gh/sarahcgallLtd) using your GitHub account.
2. Add your repository to Codecov (it will guide you).
3. Go to Coverage tab, select 'Pytest' and follow instructions.
4. Add repository token to GitHub repository (Settings --> Secrets and variables --> Actions --> Repository secrets)
5. Push changes — GitHub Actions will run the coverage workflow.
6. View reports on Codecov dashboard; add the badge to your README (uncomment below).
7. On PRs, Codecov will comment with coverage diffs.

To run coverage locally and in CI:
```bash
# Run tests with coverage locally (generates report in console and .coverage file)
poetry run pytest --cov=src/package_name

# Generate XML report for Codecov (as used in workflow)
poetry run pytest --cov=src/package_name --cov-report=xml
```

**Add Badges to README.md (e.g., for CI, coverage):**

- CI: [![CI](https://github.com/sarahcgallLtd/python-package-template/actions/workflows/ci.yml/badge.svg)](https://github.com/sarahcgallLtd/python-package-template/actions/workflows/ci.yml)
- Coverage: Set up codecov.io and add [![codecov](https://codecov.io/gh/sarahcgallLtd/python-package-template/graph/badge.svg)](https://codecov.io/gh/sarahcgallLtd/python-package-template)
- Version: [![PyPI version](https://badge.fury.io/py/python-package-template.svg)](https://badge.fury.io/py/python-package-template)

Replace `YOUR_TOKEN` with your actual Codecov token if needed (for badge auth, but often optional). Update the repo path.


## IF NEEDED: Prepare your system
Check for the latest version of Python on the Python website.
Compare in a terminal and install the latest if needed (recommend Python 3.10+).


```bash
# Check your version
python --version
# Python 3.12.6
```

Install required tools:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
# OR
pip install poetry

# Install dev dependencies globally if needed (but Poetry handles per-project)
pip install pre-commit black flake8 pytest sphinx
```

Configure Poetry (optional, for defaults):
```bash
poetry config virtualenvs.in-project true  # Keeps .venv in project root
```

Set up pre-commit hooks (optional, for auto-linting):
```bash
pre-commit install
```

Finally, verify your setup:
```bash
import sys
import poetry_version  # If installed, or just check manually

print(sys.version)
# Example output: 3.12.3 (main, Apr  9 2024, 20:09:14) [GCC 13.2.0]
```


## Best Practices

- Use virtual environments via Poetry.
- Add type hints and docstrings.
- For documentation, consider adding Sphinx.
- License: MIT (feel free to change).

For more, see [Poetry docs](https://python-poetry.org/docs/).