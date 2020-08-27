(07-ci-cd)=
# Continuous Integration and Deployment

If you've gotten this far, you have a working Python package that you've started sharing with the world! We went through quite a lot to get here: developing code, writing documentation, running tests, versioning, etc. As you continue to develop your package into the future it would be great to automate processes like testing, building, and deploying so you can focus on improving your code - this is where **continuous integration** and **continuous deployment** come in (CI/CD)! The term CI/CD generally refers to the automated testing, building, and deploying of software which we'll explore in this chapter.

```{note}
The CD part of CI/CD is also often referred to as "continuous delivery". Continuous delivery and continuous deployment have slightly different definitions: continuous delivery refers to preparing software for manual release by the developer, whereas continuous deployment takes this one step further and automates the release process too. We'll be referring to "continuous deployment" in this chapter.
```

(07-ci-cd-tools)=
## CI/CD Tools

You could implement a CI/CD workflow locally by building and testing code updates on your personal computer before pushing and deploying it to a remote repository, but this process is not reproducible or scalable, and does not work if more than one person (you) is contributing to your code (which is typically the idea if you've decided to share your code as a package). It is therefore more common to use a CI/CD service to implement CI/CD. There are many tools/companies out there that offer CI/CD implementation - the one we'll be advocating for in this book is [GitHub Actions](https://docs.github.com/en/actions), which is easy to implement and set up directly in your GitHub repository.

(07-ci)=
## Continuous Integration

Continuous integration (CI) refers to the process of continuously testing your code as it is updated, to make sure that your update doesn't cause unexpected errors. The CI process may include workflows such as style checks, custom tests, code coverage and build tests, amongst others. There are plenty of good resources available if you wish to learn more about CI, for example, the [GitHub Actions documentation](https://docs.github.com/en/actions/building-and-testing-code-with-continuous-integration/about-continuous-integration). In the remainder of this section, we'll implement CI on the `pypkgs` Python package we've been developing throughout this book.

(07-ci-set-up)=
### Set Up

Back in {ref}`02-whole-game` when we used the [UBC-MDS cookiecutter template](https://github.com/UBC-MDS/cookiecutter-ubc-mds) to create our Python package `pypkgs`, we chose to **not** include a GitHub Actions workflow file in our package template. Recall the following exerpt from when we were specifying cookiecutter template options in Section {ref}`02-cookiecutter-poetry`:

```bash
Select include_github_actions:
1 - no
2 - build
3 - build+deploy
Choose from 1, 2, 3 [1]: 1
```

This selection was made on purpose, so we could demonstrate the process of setting up GitHub Actions from scratch in this section, but in the future, feel free to include the workflow file(s) in your initial cookiecutter package set up by choosing a different option (which option you should choose will become clear after reading this chapter).

The first thing we need to do is add a "workflow" file to our repository. GitHub Actions uses `.yml` files to specify workflow files and they should be added to a subdirectory named `.github/workflows`. Go ahead and create a new file in that location called `build.yml`, you could do this from the command line with:

```bash
$ mkdir -p .github/workflows
$ touch .github/workflows/build.yml
```

Your package directory structure should now look something like this:

```
pypkgs
├── CONDUCT.rst
├── CONTRIBUTING.rst
├── CONTRIBUTORS.rst
├── docs
├── pypkgs
├── .gitignore
├── .github
│   └── workflows
│       └── build.yml
├── LICENSE
├── pyproject.toml
├── .readthedocs.yml
├── README.md
└── tests
```

Open the new `build.yml` file in an editor of your choice. We are going to set up CI that triggers every time somebody makes a push or a pull-request to the `master` branch of your repository. To set this up, copy and paste the following text, which should be fairly self-explantory, into `build.yml`:

```
name: build

on:
  # Trigger the workflow on push or pull request to master
  push:
    branches:
      - master
  pull_request:
    branches:
      - master
```

```{note}
We won't discuss the syntax of GitHub Actions .`yml` files here, but instead, refer readers to the excellent [GitHub Actions documentation](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions) on workflow file syntax.
```

Now we are going to set up our CI for a variety of different Python versions and operating systems. It's up to you which versions of Python and which operating systems you wish to support for your package - here we will want to run our tests and build our package on `Ubuntu`, `MacOS`, and `Windows` for Python versions `3.7` and `3.8`. To set this up, copy and paste the following text into `build.yml`, below the previous text:

```
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.7, 3.8]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
```

Take a moment to read through the text above. The `matrix` syntax used here allows us to perform multiple runs of our CI workflow for different versions of Python and different operating systems. Read more about the `matrix` syntax [here in the GitHub Actions documentation](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idstrategymatrix). The text `actions/checkout@v2` is a required action that "checks-out" your repository so that your workflow can access it. Read more aboue the action here in the [GitHub Actions documentation](https://docs.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#using-the-checkout-action).

We then move on to specifying the first two steps of our workflow. The first step is named "Set up Python" which simply installs the specified version of Python. The second step is named "Install dependencies" and it sets up our `poetry` environment and installs our package's dependencies (which are listed in the `poetry.lock` file in our repository). These two steps set up our workflow for automated testing and building. We will populate our CI pipeline with three actions; style checking, running tests, and recording test coverage - all of which are described below.

(07-ci-style)=
### Style Checking

The first thing we want to check is that any new code adheres to our enforced style guide. Code style is about making your code as readable as possible to humans and is incredibly important when sharing your code with other users (including your future self!). Remember, “Code is read much more often than it is written”. The Python Style Guide is outlined in [PEP 8](https://www.python.org/dev/peps/pep-0008/). It is worth taking the time to read through the PEP 8 style guidelines, but here are a few highlights:

- Indent using 4 spaces;
- Have whitespace around operators, e.g. `x = 1` not `x=1`;
- But avoid extra whitespace, e.g. `f(1)` not `f (1)`;
- Variable and function names use `underscores_between_words`;
- and much more...

Luckily, you don't have to remember all these guidelines as there are many tools out there to help you! [Flake8](https://flake8.pycqa.org/en/latest/#) is one of the most popular style guide enforcement tools and we'll use it to enforce style in our code here. First, add `flake8` as a development dependency to your package:

```bash
$ poetry add --dev flake8
```

We can now check that our code conforms to `flake8` by using the following command from our package's root directory:

```bash
$ poetry run flake8 ./

./tests/test_pypkgs.py:42:1: W391 blank line at end of file
./pypkgs/pypkgs.py:35:80: E501 line too long (86 > 79 characters)
```

```{note}
In the command above we are pointing `flake8` to our packages entire directory, within which it will search for and assess every .py file. You can also choose to point `flake8` only to a specific file, e.g., `poetry run flake8 ./pypkgs/pypkgs.py`.
```

In the output above we can see that `flake8` noticed two style violations, one in `./tests/test_pypkgs.py` and one in `./pypkgs/pypkgs.py`. We can now go into the editor of our choice and fix these violations up.

```{note}
`flake8` does not format your code, only scans it for style. However, auto-formatters that actually re-structure your code do exist, one that we use quite often is [black](https://black.readthedocs.io/en/stable/).
```

Once you can run `flake8` without getting any violations back you should push your code to GitHub. We can now include this `flake8` testing as a step in our CI pipeline by adding the following code to our `build.yml` file, directly under the existing content of that file:

```
    - name: Check style
      run: poetry run flake8 --exclude=docs*
```

Every time somebody pushes code updates or makes a pull request to the `master` branch of our repository, the code will be checked using `flake8` - great!

```{note}
Once we've added a few more steps to our CI pipeline we'll go and see it all in action on GitHub!
```

(07-ci-tests)=
### Running Tests

Remember all the hard work we put into writing tests for our package back in the chapter {ref}`04-testing`? Well, we likely want to make sure that these tests (and any others that we add) continue to pass for any new updates to our code. Just like we did with `flake8` we can automatically run our tests every time somebody pushes code updates or makes a pull request to our repository. The set up here is pretty easy! Recall that we used `pytest` as our testing framework (see section {ref}`04-test-structure`), and this is listed as a development dependency for our package so will already be installed by our CI workflow in the "Install dependencies" step. Therefore, we just need to add the `pytest` command as a step in our `build.yml` file:

```
    - name: Test with pytest
      run: poetry run pytest --cov=./ --cov-report=xml
```

Note that we are also asking for our test coverage through the `--cov` argument. We will use this in the next step to automate the recording of test coverage for our package.

```{tip}
If you're unfamiliar with recording code coverage, see section {ref}`04-code-coverage`.
```

(07-ci-coverage)=
### Recording Code Coverage

In the previous step we ran our custom-built tests for our package. An important part of the testing workflow is evaluating and keeping a record of our test's code coverage (i.e., how many lines of our code were actually executed by our tests). There are quite a few services out there for helping you do this, but we're going to use the free service of [Codecov](https://codecov.io/). We're also going to leverage a [pre-made GitHub Action workflow provided by Codecov](https://github.com/marketplace/actions/codecov) to help us record our tests and so we don't have to write too much content in our `.yml` file. All that is required is to add the following step to our `build.yml` file:

```
    - name: Upload coverage to Codecov  
      uses: codecov/codecov-action@v1
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        yml: ./codecov.yml 
        fail_ci_if_error: true
```

```{attention}
If your GitHub repository is public, then no further action is needed. However if you're repository is private, you'll need to provide an "upload token" in your repository settings as described in the [Codecov GitHub Action documentation](https://github.com/marketplace/actions/codecov). 
```

(07-ci-together)=
### Putting It All Together

Nice work! We've set up our CI pipeline. Your final `.github/workflows/build.yml` file should look like this:

```
name: build

on:
  # Trigger the workflow on push or pull request to master
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.7, 3.8]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    - name: Check style
      run: poetry run flake8 --exclude=docs*
    - name: Test with pytest
      run: poetry run pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov  
      uses: codecov/codecov-action@v1
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

If you haven't already done so, push this file to GitHub:

```bash
$ git add .
$ git commit -m "add GH actions CI workflow"
$ git push
```

As we have configured our CI pipeline to trigger on any code changes pushed to the `master` branch your workflow should have started as soon as you successfully pushed to GitHub. Head over to your repository and click on the "Actions" tab. You'll see your CI workflow in progress (or maybe already completed!):

```{figure} img/07-ci-cd/gh-build-1.png
---
width: 600px
name: gh-build-1
---
Continuous Integration (CI) pipeline running on GitHub.
```

You can click on any workflow to view it's status:

```{figure} img/07-ci-cd/gh-build-2.png
---
width: 600px
name: gh-build-2
---
Continuous Integration (CI) pipeline running on GitHub, with 4 jobs completed and 2 in progress.
```

And can even click on each individual job to see it running in real time:

```{figure} img/07-ci-cd/gh-build-3.png
---
width: 600px
name: gh-build-3
---
Continuous Integration (CI) pipeline running on GitHub. The Python 3.7, Ubuntu build is open, showing the execution of the "Test with pytest" step.
```

(07-cd)=
## Continuous Deployment

Whereas CI verifies that your updated code is working as expected, Continuous Deployment (CD) takes that updated code and deploys it into production. In the case of Python packaging, that typically means building and pushing an updated package version to PyPI. In the chapter {ref}`06-versioning` we discussed how to version and release a Python package. Here, we are going to automate this process with a GitHub Actions workflow.

```{note}
Some developers prefer to manually deploy their product rather than automate deployment with CD. However, they'll still use the terms CI/CD - typically the CD here stands for "Continuous Delivery" which essentially gets the product deployment-ready, but requires the developer to manually "push a button" to deploy the software.
```

1. version package
2. build
3. deploy

```bash
$ poetry add --dev python-semantic-release
```

(07-cd-testpypi)=
### Continuous Deployment to TestPyPI

As before in section {ref}`07-ci`, let's start by creating a new workflow file called `deploy.yml` in the `.github/workflows/` sub-directory. You can do this from the command line with:

```bash
$ mkdir -p .github/workflows
$ touch .github/workflows/deploy.yml
```

We want to trigger a deployment each time updated code is pushed to the `master` branch, and for the purpose of this workflow, we are going to run our workflow for just Python 3.7 and the Ubuntu OS. It also makes sense to run the same tests we ran in the CI pipeline here, such as code style checking, tests and coverage. Add all of this configuration by copy-pasting the below into `deploy.yml`:

```
name: deploy

on:
  # Trigger the workflow on push or pull request to master
  push:
    branches:
      - master

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.7
      uses: actions/setup-python@v1
      with:
        python-version: 3.7
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    - name: Check style
      run: poetry run flake8 --exclude=docs*
    - name: Test with pytest
      run: poetry run pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov  
      uses: codecov/codecov-action@v1
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

This is where the CD fun begins. There's four key steps we need to take care of in our CD workflow:

1. Bump the package version;
2. Create a new release on GitHub;
3. Build the package; and,
4. Release the package to TestPyPI.

#### Bump the Package Version

To automatically bump our package version we are going to use the [Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/) (PSR) tool. Put very simply, this tool is able to parse commit messages to determine if a package has been updated with, for example, a patch, minor, or major release (see section {ref}`06-version-numbering`) and bump the package version number accordingly. To use PSR, we need to add it as a development dependency of our package:

```bash
$ poetry add --dev python-semantic-release
```

We also need to configure the tool in our `pyproject.toml` file by adding the following text:

```
[tool.semantic_release]
version_variable = "pypkgs/__init__.py:__version__"
version_source = "commit"
upload_to_pypi = "false"
patch_without_tag = "true"
```

You can read more about these different configuration options in the [PSR documentation](https://python-semantic-release.readthedocs.io/en/latest/configuration.html), but briefly, the configuration above is telling PSR where our version number is located (in our case, its at `pypkgs/__init.py__`) and that we don't want to upload to PyPI (PSR uses [twine](https://pypi.org/project/twine/) as a Python packaging tool, but we will be using `poetry`).

Once we've added that configuration, we're ready to add automatic versioning as a step in our `deploy.yml` workflow file. You can do that by copy-pasting the following text into `deploy.yml`:

```
    - name: checkout
      uses: actions/checkout@master
    - name: Bump version and tagging and publish
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git pull origin master
        poetry run semantic-release version
        poetry version $(grep "version" */__init__.py | cut -d "'" -f 2 | cut -d '"' -f 2)
        git commit -m "Bump versions" -a
    - name: Push package version changes
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
```

Take a minute to read through the steps in the workflow above. Essentially, what we are doing is checking out our master branch, updating our package version in `__init__.py` (with `poetry run semantic-release version`), updating our package version in `pyproject.toml` (with the help of some regex and the command `poetry version $(grep "version" */__init__.py | cut -d "'" -f 2 | cut -d '"' -f 2)`), and then committing the updated package version back to master.

#### Create a New Release on GitHub

Now that the hard part of automatic version bumping is down we can [create a release on GitHub](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository). Luckily there's a pre-made GitHub Action for this that we can leverage. All we need to do is add the following to our `deploy.yml` file:

```
    - name: Get release tag version from package version
      run: |
        echo ::set-output name=release_tag::$(grep "version" */__init__.py | cut -d "'" -f 2 | cut -d '"' -f 2)
      id: release
    - name: Create Release with new version
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.release.outputs.release_tag }}
        release_name: ${{ steps.release.outputs.release_tag }}
        draft: false
        prerelease: false
```

Above, we are printing our release version to the console log (so we have a record of what happened!) and then creating a release with the `create-release` GitHub Action.

```{tip}
Check out the `create-release` [GitHub Action documentation](https://github.com/actions/create-release) to learn more about how this action works.
```

#### Build and Release Updated Package

The final step in our workflow is to build our package and release it to TestPyPI. We've seen the `poetry` commands for this process before in section {ref}`07-release-version`. However, because we are using a GitHub Action here to automatically push releases to TestPyPI, we'll need to provide the following two [GitHub secrets](https://docs.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) to our GitHub repository:

- TEST_PYPI_USERNAME
- TEST_PYPI_PASSWORD

```{figure} img/07-ci-cd/gh-secrets.png
---
width: 600px
name: gh-secrets
---
GitHub Secrets required for automated publishing to TestPyPI.
```

```{tip}
PyPI and TestPyPI now also support the use of an API token, which can be used instead of a username and password. Read more in the [official documentation](https://pypi.org/help/#apitoken).
```

Once that's done, simply add the following text to the `deploy.yml` file and we're done!

```
    - name: Build package and publish to test PyPI
      env:
        TEST_PYPI_USERNAME: __token__ 
        TEST_PYPI_PASSWORD: ${{ secrets.TEST_PYPI_PASSWORD }}
      run: |
        poetry config repositories.test-pypi https://test.pypi.org/legacy/
        poetry build
        poetry publish -r test-pypi -u $TEST_PYPI_USERNAME -p $TEST_PYPI_PASSWORD
```

#### Testing the CD Workflow 

Nice work! We've set up our CD pipeline. Your final `.github/workflows/build.yml` file should look like this:

```
name: deploy

on:
  # Trigger the workflow on push or pull request to master
  push:
    branches:
      - master

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.7
      uses: actions/setup-python@v1
      with:
        python-version: 3.7
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    - name: Check style
      run: poetry run flake8 --exclude=docs*
    - name: Test with pytest
      run: poetry run pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov  
      uses: codecov/codecov-action@v1
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
    - name: checkout
      uses: actions/checkout@master
    - name: Bump version and tagging and publish
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git pull origin master
        poetry run semantic-release version
        poetry version $(grep "version" */__init__.py | cut -d "'" -f 2 | cut -d '"' -f 2)
        git commit -m "Bump versions" -a
    - name: Push package version changes
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
    - name: Get release tag version from package version
      run: |
        echo ::set-output name=release_tag::$(grep "version" */__init__.py | cut -d "'" -f 2 | cut -d '"' -f 2)
      id: release
    - name: Create Release with new version
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.release.outputs.release_tag }}
        release_name: ${{ steps.release.outputs.release_tag }}
        draft: false
        prerelease: false
    - name: Build package and publish to test PyPI
      env:
        TEST_PYPI_USERNAME: ${{ secrets.TEST_PYPI_USERNAME }} 
        TEST_PYPI_PASSWORD: ${{ secrets.TEST_PYPI_PASSWORD }}
      run: |
        poetry config repositories.test-pypi https://test.pypi.org/legacy/
        poetry build
        poetry publish -r test-pypi -u $TEST_PYPI_USERNAME -p $TEST_PYPI_PASSWORD

```

If you haven't already done so, push this file to GitHub:

```bash
$ git add .
$ git commit -m "add GH actions CD workflow"
$ git push
```

As we have configured our CD pipeline to trigger on any code changes pushed to the `master` branch your workflow should have started as soon as you successfully pushed to GitHub. Head over to your repository and click on the "Actions" tab. You'll see your CD workflow in progress (or maybe already completed!):

```{figure} img/07-ci-cd/gh-deploy-1.png
---
width: 600px
name: gh-deploy-1
---
Continuous Deployment (CD) pipeline running on GitHub.
```

We can inspect the log of our CD workflow to see exactly where our package version update occurred:

```{figure} img/07-ci-cd/gh-deploy-2.png
---
width: 600px
name: gh-deploy-2
---
Continuous Deployment (CD) pipeline log on GitHub, showing the automated version bumping step.
```

Over at TestPyPI, we can also see that our package has been successfully updated!

```{figure} img/07-ci-cd/gh-testpypi.png
---
width: 600px
name: gh-testpypi
---
The `pypkgs` Python package updated to version 0.1.2 on [TestPyPI](https://test.pypi.org/).
```

In this case, our package was bumped from version `0.1.1` to `0.1.2` because our [Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/) versioning tool decided that, based on our commit message, this should be a patch release. You can read more about what kind of words in a commit message trigger different types of releases in the [Python Semantic Release documentation](https://python-semantic-release.readthedocs.io/en/latest/commit-log-parsing.html). As an example, we can trigger a minor release by using the syntax "feat: my commit message" in our commit message. Let's try that now by making a change to one of our files (I made a change to `README.md`).

```{attention}
You will also need to update the version-checking test in `tests/test_pypkgs.py`. While our `deploy.yml` workflow updates our package version in `pypkgs/__init__/py`, we do not have it configured to update the version in `tests/test_pypkgs.py`, so if you ran `poetry run pytest`, the tests would fail. It's easy to add the version number in `test_pypkgs.py` as a variable for Python Semantic Release to also update through `deploy.yml` (see the documentation [here]). But I prefer to make the change manually to avoid unintentionally incrementing version numbers with small commits. You could also choose to simply remove the version-checking test from `tests/test_pypkgs.py`.
```

Once you've made any desired changes, commit and push them with the following commit message to trigger a minor release:

```bash
$ git add .
$ git commit -m "feat: big updates to readme.md"
$ git push
```

You can check the GitHub Action workflow logs, GitHub repository or TestPyPI to make sure your minor release was successful!

```{figure} img/07-ci-cd/gh-minor.png
---
width: 600px
name: gh-minor
---
The `pypkgs` Python package updated with a minor release to version 0.2.0.
```

```{figure} img/07-ci-cd/gh-testpypi-minor.png
---
width: 600px
name: gh-testpypi-minor
---
The `pypkgs` Python package updated to version 0.2.0 on [TestPyPI](https://test.pypi.org/).
```

(07-cd-pypi)=
### Continuous Deployment to PyPI

If you'd prefer to deploy your package to PyPI as opposed to TestPyPI, you can easily do that by changing the workflow section named "Build package and publish to test PyPI" to:

```
    - name: Build package and publish to PyPI
      env:
        PYPI_USERNAME: ${{ secrets.PYPI_USERNAME }} 
        PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        poetry build
        poetry publish -u $PYPI_USERNAME -p $PYPI_PASSWORD
```

```{tip}
Don't forget to add PYPI_USERNAME and PYPI_PASSWORD as [GitHub secrets](https://docs.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) in your repository.
```

(07-ci-cd-summing)=
## Summing Up

CI/CD is a great way to streamline your package development and open-source collaboration. In this chapter we've walked through a simple CI/CD workflow for a Python package using tools like `poetry`, GitHub Actions, and Python Semantic Release. These, and other, tools can be configured in many different ways to achieve almost any workflow imaginable! Good luck and enjoy the automation and freedom that CI/CD (hopefully) provides!