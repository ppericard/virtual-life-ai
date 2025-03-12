# Contributing to VirtualLife

Thank you for considering contributing to VirtualLife! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

1. Check the issue tracker to see if the bug has already been reported.
2. If you're unable to find an open issue addressing the problem, open a new one using the bug report template.

When filing an issue, include:

- A clear title and description
- As much relevant information as possible (Python version, operating system, etc.)
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots or code snippets if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues:

1. Check the issue tracker to see if the enhancement has already been suggested.
2. If not, open a new issue using the feature request template.

Include:

- A clear title and description
- The rationale for the enhancement
- Description of the current behavior and expected behavior
- Any relevant examples or mock-ups

### Your First Code Contribution

Unsure where to begin? Look for issues tagged with:

- `good-first-issue`: Issues suitable for newcomers
- `help-wanted`: Issues that need assistance
- `documentation`: Improvements or additions to documentation

### Pull Requests

1. Fork the repository
2. Create a new branch with a descriptive name
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as needed
6. Ensure all tests pass and code quality checks succeed
7. Submit a pull request

## Development Process

### Setting Up the Development Environment

Follow the instructions in [SETUP.md](SETUP.md) to set up your development environment.

### Coding Standards

This project follows these coding standards:

- Code formatting with Black (line length 88)
- Import sorting with isort
- Type annotations for all functions and classes
- Google-style docstrings for all public APIs
- Comprehensive test coverage

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or fewer
- Reference issues and pull requests after the first line

Example:
```
Add environment boundary conditions

Implement wrapped, bounded, and infinite boundary conditions for the grid environment.
Fixes #42
```

### Branch Naming Convention

- Feature branches: `feature/short-description`
- Bug fix branches: `fix/issue-description`
- Documentation branches: `docs/what-is-being-documented`
- Performance improvement branches: `perf/what-is-being-improved`

### Testing

All new code should include tests. Run the test suite before submitting a pull request:

```bash
pytest
```

### Documentation

- Update documentation for new features or changes to existing functionality
- If adding a new feature, include examples of how to use it
- Update the API reference for public APIs

## Releasing

The release process is managed by the maintainers. Releases follow [Semantic Versioning](https://semver.org/).

## Getting Help

If you need help, you can:

- Open an issue with the question tag
- Reach out to the maintainers
- Check the documentation

Thank you for contributing to VirtualLife! 