import pytest

from hypothesis import HealthCheck, settings, Verbosity

from convclasses import Converter


@pytest.fixture()
def converter():
    return Converter()


settings.register_profile(
    "tests",
    suppress_health_check=(HealthCheck.too_slow, HealthCheck.filter_too_much),
    deadline=None,
    verbosity=Verbosity.verbose,
)

settings.load_profile("tests")
