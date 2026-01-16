"""Tests for the Tacomail CLI plain output functionality."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typer.testing import CliRunner

from tacomail.cli import app
from tacomail import Email, Session


runner = CliRunner()


@pytest.fixture
def mock_email():
    """Create a mock Email object for testing."""
    email = MagicMock(spec=Email)
    email.id = "test-email-id-123"
    email.subject = "Test Subject"
    email.date = datetime(2024, 1, 15, 10, 30, 0)
    email.from_ = MagicMock()
    email.from_.name = "Sender Name"
    email.from_.address = "sender@example.com"
    email.to = MagicMock()
    email.to.name = "Recipient Name"
    email.to.address = "recipient@example.com"
    email.body = MagicMock()
    email.body.text = "This is the email body."
    email.attachments = []
    return email


@pytest.fixture
def mock_session():
    """Create a mock Session object for testing."""
    session = MagicMock(spec=Session)
    session.username = "testuser"
    session.domain = "tacomail.de"
    session.expires = 1705320600000  # Some future timestamp in milliseconds
    return session


class TestCreatePlainOutput:
    """Tests for the 'create' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_create_plain_output(self, mock_get_client):
        """Test that create command outputs just the email address in plain mode."""
        mock_client = MagicMock()
        mock_client.get_random_address.return_value = "random123@tacomail.de"
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "create"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "random123@tacomail.de"
        # Should not contain Rich formatting
        assert "✨" not in result.stdout
        assert "[bold" not in result.stdout

    @patch("tacomail.cli.get_client")
    def test_create_with_domain_plain_output(self, mock_get_client):
        """Test create command with domain option in plain mode."""
        mock_client = MagicMock()
        mock_client.get_random_username.return_value = "randomuser"
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "create", "-d", "tacomail.de"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "randomuser@tacomail.de"


class TestListDomainsPlainOutput:
    """Tests for the 'list-domains' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_list_domains_plain_output(self, mock_get_client):
        """Test that list-domains outputs one domain per line in plain mode."""
        mock_client = MagicMock()
        mock_client.get_domains.return_value = ["tacomail.de", "example.com", "test.org"]
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "list-domains"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert lines == ["tacomail.de", "example.com", "test.org"]
        # Should not contain Rich formatting
        assert "•" not in result.stdout
        assert "[bold" not in result.stdout


class TestCreateSessionPlainOutput:
    """Tests for the 'create-session' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_create_session_plain_output(self, mock_get_client, mock_session):
        """Test that create-session outputs key=value format in plain mode."""
        mock_client = MagicMock()
        mock_client.create_session.return_value = mock_session
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "create-session", "testuser@tacomail.de"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "email=testuser@tacomail.de" in lines
        assert "username=testuser" in lines
        assert "domain=tacomail.de" in lines
        assert any(line.startswith("expires=") for line in lines)
        # Should not contain Rich formatting
        assert "🔐" not in result.stdout


class TestDeleteSessionPlainOutput:
    """Tests for the 'delete-session' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_delete_session_plain_output(self, mock_get_client):
        """Test that delete-session outputs deleted=email in plain mode."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "delete-session", "testuser@tacomail.de"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "deleted=testuser@tacomail.de"
        # Should not contain Rich formatting
        assert "✓" not in result.stdout


class TestListInboxPlainOutput:
    """Tests for the 'list' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_list_inbox_plain_output(self, mock_get_client, mock_email):
        """Test that list outputs tab-separated values in plain mode."""
        mock_client = MagicMock()
        mock_client.get_inbox.return_value = [mock_email]
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "list", "testuser@tacomail.de"])

        assert result.exit_code == 0
        # Output should be tab-separated: id, from_address, subject, date
        line = result.stdout.strip()
        parts = line.split("\t")
        assert len(parts) == 4
        assert parts[0] == "test-email-id-123"
        assert parts[1] == "sender@example.com"
        assert parts[2] == "Test Subject"

    @patch("tacomail.cli.get_client")
    def test_list_inbox_empty_plain_output(self, mock_get_client):
        """Test that empty inbox produces no output in plain mode."""
        mock_client = MagicMock()
        mock_client.get_inbox.return_value = []
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "list", "testuser@tacomail.de"])

        assert result.exit_code == 0
        assert result.stdout.strip() == ""


class TestGetEmailPlainOutput:
    """Tests for the 'get' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_get_email_plain_output(self, mock_get_client, mock_email):
        """Test that get outputs key=value format in plain mode."""
        mock_client = MagicMock()
        mock_client.get_email.return_value = mock_email
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "get", "testuser@tacomail.de", "email-id"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "id=test-email-id-123" in lines
        assert "from=sender@example.com" in lines
        assert "from_name=Sender Name" in lines
        assert "to=recipient@example.com" in lines
        assert "to_name=Recipient Name" in lines
        assert "subject=Test Subject" in lines
        assert "body=This is the email body." in lines
        # Should not contain Rich formatting
        assert "📧" not in result.stdout


class TestDeleteEmailPlainOutput:
    """Tests for the 'delete' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_delete_email_plain_output(self, mock_get_client):
        """Test that delete outputs deleted=id in plain mode."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "delete", "testuser@tacomail.de", "email-id-123"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "deleted=email-id-123"


class TestClearInboxPlainOutput:
    """Tests for the 'clear' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_clear_inbox_plain_output(self, mock_get_client):
        """Test that clear outputs cleared=email in plain mode (no confirmation needed)."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "clear", "testuser@tacomail.de"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "cleared=testuser@tacomail.de"


class TestWaitPlainOutput:
    """Tests for the 'wait' command plain output."""

    @patch("tacomail.cli.get_client")
    def test_wait_plain_output_success(self, mock_get_client, mock_email):
        """Test that wait outputs key=value format in plain mode when email received."""
        mock_client = MagicMock()
        mock_client.wait_for_email.return_value = mock_email
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "wait", "testuser@tacomail.de", "-t", "1"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "id=test-email-id-123" in lines
        assert "from=sender@example.com" in lines
        assert "subject=Test Subject" in lines
        # Should not have the waiting message
        assert "Waiting for email" not in result.stdout

    @patch("tacomail.cli.get_client")
    def test_wait_plain_output_timeout(self, mock_get_client):
        """Test that wait outputs timeout=true in plain mode when no email."""
        mock_client = MagicMock()
        mock_client.wait_for_email.return_value = None
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "wait", "testuser@tacomail.de", "-t", "1"])

        assert result.exit_code == 1
        assert "timeout=true" in result.stdout

    @patch("tacomail.cli.get_client")
    def test_wait_plain_output_with_body(self, mock_get_client, mock_email):
        """Test that wait with --print-body includes body in plain mode."""
        mock_client = MagicMock()
        mock_client.wait_for_email.return_value = mock_email
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "wait", "testuser@tacomail.de", "-t", "1", "--print-body"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "body=This is the email body." in lines


class TestCreateWithSessionPlainOutput:
    """Tests for the 'create-with-session' and 'new' commands plain output."""

    @patch("tacomail.cli.get_client")
    def test_create_with_session_plain_output(self, mock_get_client, mock_session):
        """Test that create-with-session outputs key=value format in plain mode."""
        mock_client = MagicMock()
        mock_client.get_random_address.return_value = "random123@tacomail.de"
        mock_client.create_session.return_value = mock_session
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "create-with-session"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "email=random123@tacomail.de" in lines
        assert "username=testuser" in lines
        assert "domain=tacomail.de" in lines
        assert any(line.startswith("expires=") for line in lines)
        # Should not contain Rich formatting or next steps
        assert "✨" not in result.stdout
        assert "Next steps" not in result.stdout

    @patch("tacomail.cli.get_client")
    def test_new_command_plain_output(self, mock_get_client, mock_session):
        """Test that 'new' command (alias) also works with plain output."""
        mock_client = MagicMock()
        mock_client.get_random_address.return_value = "random123@tacomail.de"
        mock_client.create_session.return_value = mock_session
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["--plain", "new"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert "email=random123@tacomail.de" in lines


class TestPlainOptionHelp:
    """Test that the --plain option is properly documented."""

    def test_plain_option_in_help(self):
        """Test that --plain option appears in CLI help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Output may contain ANSI escape codes, so search for "plain" which should appear
        assert "plain" in result.stdout.lower()
        assert "easy parsing" in result.stdout.lower() or "parsing" in result.stdout.lower()
