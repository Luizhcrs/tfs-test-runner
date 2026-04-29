"""Regenerate examples/blank-template.xlsx from the bundled package generator.

Output: examples/blank-template.xlsx

Usage:
    python examples/generate_blank_template.py

Note: blank-template.xlsx is gitignored. CI and `pip install` users obtain
the file via `tfs-test-runner init`, which generates it at runtime via
`tfs_test_runner.templates.write_blank_xlsx`. This script is for repo
maintainers who want a checked-in copy.
"""
from pathlib import Path
from tfs_test_runner.templates import write_blank_xlsx

if __name__ == "__main__":
    out = Path(__file__).parent / "blank-template.xlsx"
    write_blank_xlsx(out)
    print(f"wrote {out}")
