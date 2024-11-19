import pytest
from click.testing import CliRunner
from moto import mock_aws

from asati.utils import SSMClient


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "None")
    monkeypatch.setenv("WORKSPACE", "test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mocked_ssm():
    with mock_aws():
        ssm = SSMClient()
        ssm.update_parameter(
            parameter_name="/apps/asati/last-accession-uri-id", parameter_value="1235"
        )
        yield ssm


@pytest.fixture
def ssm_client():
    return SSMClient()
