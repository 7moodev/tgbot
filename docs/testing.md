# Best Practices

- Follow Naming Conventions
- Test files: test\_<module>.py
- Test functions: test\_<functionality>()
- Use Assertions
- Use assert in pytest, or self.assertEqual() in unittest.
- Test Edge Cases
- Cover normal, boundary, and error conditions.
- Keep Tests Isolated
- Avoid dependencies between tests.
- Use Fixtures (pytest.fixture)
- For reusable setup logic.
- Mock External Dependencies
- Use unittest.mock or pytest-mock.
- Automate Test Running
- Use pytest with tox or pre-commit hooks.
- Continuous Integration (CI)
- Run tests in GitHub Actions, GitLab CI, etc.

# Libraries
- test runners (such as pytest),
- linters (e.g., flake8),
- formatters (for example black or isort),
- documentation generators (e.g., Sphinx),
- build and publishing tools (e.g., build with twine),
