"""COMPOSER-160 Validation Module.

Exposes the Validator class and CheckResult dataclass for enforcing
the C1–C7 self-check constraints.
"""

from composer160.validation.checks import CheckResult, Validator

__all__ = ["CheckResult", "Validator"]
