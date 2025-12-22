from ai_guard.rules.dependency_hygiene import DependencyHygieneRule
from ai_guard.rules.python_security import PythonSecurityRule
from ai_guard.rules.secret_logging import SecretLoggingRule

DEFAULT_RULES = [
    PythonSecurityRule(),
    SecretLoggingRule(),
    DependencyHygieneRule(),
]
