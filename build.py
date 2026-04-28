"""Convenience shim: python build.py input.xlsx -o output.html [...]

Equivalent to: tfs-test-runner input.xlsx -o output.html
After `pip install -e .` you can use the `tfs-test-runner` console script.
"""
from tfs_test_runner.cli import main

if __name__ == "__main__":
    main()
