# Changelog

<!--next-version-placeholder-->

## v0.5 (09/02/202)

✨NEW
- **Section 2.6: Developing with Docker**. Instructions on how to set up a package development environment in VS Code or Jupyter with the help of Docker. Closes #101
- **Section 3.6.1: Dependency version constraints**. Discusses what version constraints are, the problems that can occur with upper caps, and why we dissuade from using them (going against the `poetry` default). Closes #95
- **Section 7.6: Updating dependency versions**. Details about how to update dependency versions for your package.
- **Chapter 8**: revised and updated workflow for CI/CD. Closes #103


♻️UPDATE
- Various updates to **Chapter 8**, fail-proofing PSR, ensuring it makes GitHub releases (currently just doing tags), cleaning up workflows files. Closes #103
- More reminders/warnings throughout the book to activate your virtual environment before running using or developing package.
- In **Section 3.3.2 Set up remote version control**, entering suername and password is no longer allowed to connect to GitHub so recommend setting up SSH auth.

## v0.4 (06/12/2021)

General updates after professional proofs:

- Python Packages will soon be available to buy with the help of our publisher CRC Press (Taylor & Francis Group).
- This version contains revisions to the book following review by CRC Press editors and an external proofreader.
- Note that the book will remain open-course and available to read online.

## v0.3 (06/09/2021)

Complete overhaul of existing chapters and content. Key notes:

- Jupyter Book being used for HTML version
- Bookdown being used for PDF version
- Closes most outstanding issues: #5 #6 #7 #8 #9 #11 #12 #15 #18 #22 #34 #38 #44 #46 #48 #49 #51 #55 #61 #69 #70 #71 #72 #78 #79 #80 #81 #82 #83 #84

## v0.2 (28/08/2021)

This is the v0.2 release of Python Packages. Key changes include:

- Added and revised content
- Moved to Jupyter Book as a build tool

## v0.1 (23/04/2021)

- This is the first release of Python Packages. It was created using Bookdown.
