"""tfs-test-runner — Azure DevOps / TFS xlsx → HTML test plan generator."""
__version__ = "2.1.3"

from .parse import parse_xlsx
from .translate import translate_cases, load_glossary_yaml, DEFAULT_MODEL
from .classify import assign_phases, apply_yaml_phases, load_yaml_phases
from .render import render

__all__ = [
    "__version__",
    "parse_xlsx",
    "translate_cases",
    "load_glossary_yaml",
    "DEFAULT_MODEL",
    "assign_phases",
    "apply_yaml_phases",
    "load_yaml_phases",
    "render",
]
