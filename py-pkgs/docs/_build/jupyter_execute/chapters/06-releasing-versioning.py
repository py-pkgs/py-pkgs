(06-versioning)=
# Releasing and Versioning

Packages exist so that you can share your code with others. Previous chapters have focussed on how to develop your Python package for distribution - we are now ready to release the package to users (which might include your future self, others in your company, or the world). In the {ref}`02-whole-game` we briefly showed how to release a package to PyPI, Python's main package index. This chapter now describes in more detail the process of releasing a package and is inspired by the [Releasing a package chapter](https://r-pkgs.org/release.html) of the [R packages book](https://r-pkgs.org/). In the follow chapter {ref}`07-ci-cd` we show how the process of developing and releasing a package can be automated.

(06-package-repositories)=
## Package Repositories

When you're ready to release your software, you first need to decide where to release it to. The Python Package Index ([PyPI](https://pypi.org/)) is the official, open-source, software repository for Python (as CRAN is the repository for R). If you're interested in sharing your work publicly, this is probably where you'll be releasing your package. 

We'll focus on releasing packages to PyPI in this chapter, however PyPI is not the only option. Another popular software repository for Python (and other languages) packages is that hosted by [Anaconda](https://www.anaconda.com/) and accessible with the [conda package manager](https://docs.conda.io/en/latest/) (which we installed back in {ref}`01-python-setup`). We won't go into the details of the differences between these two popular repositories here, but if you're interested to read more, we recommend [this article](https://www.anaconda.com/blog/understanding-conda-and-pip#:~:text=Pip%20installs%20Python%20packages%20whereas,software%20written%20in%20any%20language.&text=Another%20key%20difference%20between%20the,the%20packages%20installed%20in%20them.). Creating packages for Anaconda requires a little more work than for PyPI - Anaconda provides a [helpful tutorial](https://docs.conda.io/projects/conda-build/en/latest/user-guide/tutorials/build-pkgs-skeleton.html) on the workflow.

In some cases, you may want to release your package to a private repository (for example, for internal use by your company only). There are many private repository options for Python packages. Companies like [Anaconda](https://docs.anaconda.com/), [PyDist](https://pydist.com/) and [GemFury](https://gemfury.com/) are all examples that offer (typically paid) private Python package repository hosting. You can also set up your own server on a dedicated machine or cloud service like AWS - read more [here](https://medium.com/swlh/how-to-install-a-private-pypi-server-on-aws-76993e45c610).

Finally, you can also choose to simply host your package on GitHub (or equivalent), and forego releasing to a dedicated software repository like PyPI. In some cases, it is possible for users to `pip install` directly from a GitHub repository (read [this excellent article](https://adamj.eu/tech/2019/03/11/pip-install-from-a-git-repository/) to learn more). For example, to install the `pypkgs` package directly from GitHub:

```bash
$ python -m pip install git+https://github.com/TomasBeuzen/pypkgs.git
```

```{attention}
We don't recommend GitHub for sharing Python packages to a wide audience as the install workflow can often be problematic, the vast majority of Python users do not install packages from GitHub, and dedicated software repositories like PyPI provide better discoverability, ease of installation and a stamp of authenticity.
```

(06-version-numbering)=
## Version Numbering

Versioning is the process of adding unique identifiers to different versions of your package. The unique identifier you use may be name-based or number-based. Python prefers number-based schemes and we saw an example of this in {ref}`02-whole-game` chapter where we assigned our `pypkgs` package an intial version number of 0.1.0 (the default when using the `poetry` package manager). This three-number versioning scheme (also referred to as semantic versioning) is the most common scheme used and the idea is to incrementally increase the version number in a logical way as you make changes to your package.

When you do make changes to your package, how do you decide how to increment the version? Will our next version be 0.1.1, 0.2.0, or 1.1.0? Here are the general guidelines for increment package version:

- Patch release (0.1.`X+1`): patches are typically small changes to your package that do not add any significant new features, for example, a small bug fix or documentation change that do not change backward compatibility (the compatibility of your package with previous versions of itself). It's fine to have so many patch releases that you need to use two (e.g., 0.1.10) or even three (e.g., 0.1.127) digits!
- Minor release (0.`X+1`.0): a minor release may include bug fixes, new package features and changes in backward compatibility.
- Major release (`X+1`.1.0): used when you make major changes that are not backward compatible and are likely to affect many users. Typically, when you come to versioning from 0.x.y to 1.0.0, this indicates that your package is feature-complete with a stable API.

Read more about semantic versioning [here](https://semver.org/). Note that there are many variations of semantic versioning. For example, often software packages will include alpha/beta/candidate release versions (e.g., 1.1.0-alpha.0) or development versions (e.g., 1.0.dev1). [PEP 440](https://www.python.org/dev/peps/pep-0440/#examples-of-compliant-version-schemes) contains examples of all the Python-compliant version identifier schemes. We'll show how to increment your package version with `poetry` in section {ref}`06-releasing`.

(06-deprecating)=
## Backward Compatibility & Deprecating Package Functionality

As discussed above, minor and major version releases often come with backward compatible changes which will affect your package's user base. The impact and importance of backward compatibility is directly proportional to the number of people using your package. That's not to say that you should avoid backward compatible changes - there are good reasons for making these changes, such as improving software design mistakes, improving functionality, or making code simpler and easier to use.

If you do need to make a backward incompatible change, it might be best to implement that change gradually, by providing adequate warning and advice to your package's user base through deprecation warnings.


For example, we can add a deprecation warning to our code quite easily by using the [`warnings` module](https://docs.python.org/3/library/warnings.html) in the Python standard library. If you've been following along with the `pypkgs` package we've been developing in this book, we could add a deprecation warning to our `catbind()` function by simpling importing the `warnings` module and adding a `FutureWarning` in our code:

```python
import pandas as pd
import warnings


def catbind(a, b):
    """
    Concatenates two pandas categoricals.

    ...
    """
    
    warnings.warn("This function will be deprecated in 1.0.0.", FutureWarning)

    if not all(isinstance(x, pd.Categorical) for x in (a, b)):
        raise TypeError("Inputs should be of type 'Pandas categorical'.")

    concatenated = pd.concat([pd.Series(a.astype("str")), pd.Series(b.astype("str"))])
    return pd.Categorical(concatenated)
```

If we were to run our code now, we would see the `FutureWarning` printed to our output. If you've used any larger Python libraries before (such as `NumPy`, `Pandas` or `scikit-learn`) you probably have seen these warnings before! On that note, these large, established Python libraries offer great resources for learning how to properly manage your own package - don't be afraid to check out their source code and history on GitHub.

```python
>>> from pypkgs import pypkgs
>>> import pandas as pd
>>> a = pd.Categorical(["character", "hits", "your", "eyeballs"])
>>> b = pd.Categorical(["but", "integer", "where it", "counts"])
>>> pypkgs.catbind(a, b)

pypkgs.py:33: FutureWarning: This function will be deprecated in version 1.0.0.
[character, hits, your, eyeballs, but, integer, where it, counts]
Categories (8, object): [but, character, counts,
eyeballs, hits, integer, where it, your]
```

A few other things to think about when making backward compatability changes:

- If you're changing a function significantly, consider keeping both the legacy (with a deprecation warning) and new version of the function for a few versions to help users make a smoother transition to using the new function.
- If you're deprecating a lot of code, consider doing it in small increments over mutliple releases.
- If your backward incompatible change is a result of one of your package's dependencies changing, it is often better to warn your users that they require a newer version of a dependency rather than immediately making it a required dependency (which might break a users' other code).
- Documentation is key! Don't be afraid to be verbose about documenting backward incompatible changes in your package documentation, remote repository, email list, etc.

(06-releasing)=
## Releasing Your Package

When you're ready to release a new version of your package, there's a few key tasks to take care of as described in the sections below.

```{tip}
If this is the first time you're releasing your package, you can skip to section {ref}`07-test-version`, or better yet, you might find it helpful to first go through the chapter {ref}`02-whole-game`.
```

(07-increment-version)=
### Increment Package Version

You'll need to bump your package's version in its metadata (and potentially elsewhere). In our current `pypkgs` package setup, which was created with the [UBC-MDS-Cookiecutter](https://github.com/UBC-MDS/cookiecutter-ubc-mds) and [`poetry`](https://python-poetry.org/), there are three places we need to change our package version:

- 1. `pyproject.toml`

The head of our `pyproject.toml` file currently looks like this:

```bash
[tool.poetry]
name = "pypkgs"
version = "0.1.0"
description = "Python package that eases the pain of concatenating Pandas categoricals!"
authors = ["Tomas Beuzen <tomas.beuzen@gmail.com>"]
license = "MIT"
readme = "README.md"
```

Say we've made a bug fix to our package and want to make a patch release (versioning from 0.1.0 to 0.1.1). `poetry` provides a simple command to help us do this:

```bash
$ poetry version patch  
Bumping version from 0.1.0 to 0.1.1
```

```{tip}
Here we've used the syntax `patch` to do a patch release, but `poetry` offers many [different kinds of version bumping](https://python-poetry.org/docs/cli/#version).
```

The head of our `pyproject.toml` file now looks like this:

```bash
[tool.poetry]
name = "pypkgs"
version = "0.1.1"
description = "Python package that eases the pain of concatenating Pandas categoricals!"
authors = ["Tomas Beuzen <tomas.beuzen@gmail.com>"]
license = "MIT"
readme = "README.md"
```
- 2. `pypkgs/__init__.py`

The version of our package is also specified in `pypkgs/__init__.py`. So we need to go into the file and change it there. It might seem a bit inefficient that `poetry` doesn't update the package version in `__init__.py`. It is possible to automate the version incrementing through `poetry` using a small hack which is discussed in [this issue thread](https://github.com/python-poetry/poetry/pull/2366) in the `poetry` GitHub repository, or you could simply remove the package version from `__init__.py` (not recommended). I personally don't mind manually changing the package version in this file as it provides me with a sanity check to make sure I'm versioning my package as I intend to.
- 3. `tests/test_pypkgs.py`

Our test file contains a test to ensure that our package version is up to date:

```python
def test_version(self):
        assert __version__ == '0.1.0'
```

We need to update this version number to '0.1.1'. This test is not necessary, but it's good practice to include it as a check to make sure that you're using the correct version of your package.

(07-test-version)=
### Test Your New Package Version

It's important to run all the necessary tests and checks on your newly versioned package before releasing it. In our case, we need to check that our package is still passing all our tests:

```bash
$ poetry run pytest

============================= test session starts ==============================
platform darwin -- Python 3.7.6, pytest-5.4.3, py-1.9.0, pluggy-0.13.1
rootdir: /Users/tbeuzen/GitHub/py-pkgs/pypkgs
collected 3 items                                                              

tests/test_pypkgs.py ..                                                  [100%]

============================== 3 passed in 0.71s ===============================
```

And that our documentation is rendering correctly:

```bash
$ cd docs
$ poetry run make html
```

However, your package (or other open-source packages) might require more checks than this, for example to determine that your code conforms to a particular code style, contains appropriate documentation, can be built on different operating systems and versions of Python, etc.

```{tip}
In the next chapter, we'll explore how to automate this checking and testing procedure with continuous integration.
```

(07-release-version)=
### Release Package

Once your package has passed all of your pre-release checks and tests you're ready to release it! In our case, we're interested in releasing our new package version on PyPI. It's good practice to release your package on [testPyPI](https://test.pypi.org/) first and to test that you can release and install the package as expected, before releasing on PyPI. As we've seen in previous sections of this book, `poetry` has a command called `publish` which we can use to do this, however the default behaviour is to publish to PyPI. So we need to add testPyPI to the list of repositories `poetry` knows about via:

```bash
$ poetry config repositories.test-pypi https://test.pypi.org/legacy/
```

Before we send our package to testPyPI, we first need to build it to source and wheel distributions (the format that PyPI distributes and something we learned about in the chapter {ref}`03-package-structure`) using `poetry build`:

```bash
$ poetry build
```

Finally, we can use `poetry publish` to publish to testPyPI (you will be prompted for your testPyPI username and password, sign up for one if you have not already done so):

```bash
$ poetry publish -r test-pypi
```

Now you should be able to visit your package on testPyPI (e.g., <https://test.pypi.org/project/pypkgs/>) and download it from there using `pip` via:

```bash
$ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pypkgs
```

```{note}
By default `pip install` will search PyPI for the named package. However, we want to search testPyPI because that is where we uploaded our package. The argument `--index-url` points `pip` to the testPyPI index. However, our package `pypkgs` depends on `pandas` which can't be found on testPyPI (it is hosted on PyPI). So, we need to use the `--extra-index-url` argument to also point `pip` to PyPI so that it can pull any necessary dependencies of `pypkgs` from there.
```

If you're happy with how your package is working, you can go ahead and publish to PyPI:

```bash
$ poetry publish
```

```{note}
In the next chapter {ref}`07-ci-cd` we'll see how we can automate the building and publishing of package releases to testPyPI and PyPI.
```

(07-document-version)=
### Document Your Release

Once you've released a new version of your package it's good practice to document what's happened. Firstly you should document what changed in this new release in a file in your local and remote repository. This file is typically called something like `CHANGELOG`, `NEWS`, or `HISTORY` and provides a summary of the changes in each version of your package. For example:

```
# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2020-07-23

### Added
- More documentation to pypkgs.catbind() function
- ...

### Removed
- ...

### Changed
- ...

## [0.1.0] - 2020-07-21

...
```

Secondly, you should [tag a release](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository) on GitHub (or whatever remote repository you are using). The tag version is typically the letter "v" followed by the package version, e.g., `v0.1.1` and the description should be a copy-paste of what was included in the change log.

```{important}
You should be regularly pushing your work to your remote repository, at least at the end of every coding session!
```