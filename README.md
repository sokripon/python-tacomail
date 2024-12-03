# Tacomail Python Client

An unofficial Python client library for [Tacomail](https://tacomail.de/), a disposable email service. This library provides both synchronous and asynchronous interfaces to interact with the Tacomail API.

## Features

- 🔄 Both synchronous and asynchronous clients
- 📧 Generate random email addresses
- 📥 Fetch and manage temporary inboxes
- 📎 Handle email attachments
- ⏱️ Wait for specific emails with filtering capabilities
- 🔍 Full type hints and dataclass models

## Installation

```bash
pip install tacomail
```

## Quick Start

### Synchronous Usage

```python
from tacomail import TacomailClient

with TacomailClient() as client:
    # Get a random email address
    username = client.get_random_username()
    domains = client.get_domains()
    email_address = f"{username}@{domains[0]}"
    
    # Wait for an email to arrive
    email = client.wait_for_email(email_address, timeout=30)
    if email:
        print(f"From: {email.from_.address}")
        print(f"Subject: {email.subject}")
        print(f"Body: {email.body.text}")
```

### Asynchronous Usage

```python
import asyncio
from tacomail import AsyncTacomailClient

async def main():
    async with AsyncTacomailClient() as client:
        # Get a random email address
        email_address = await client.get_random_address()
        
        # Wait for an email with specific subject
        def filter_email(email):
            return email.subject == "Welcome!"
            
        email = await client.wait_for_email_filtered(
            email_address,
            filter_fn=filter_email,
            timeout=30
        )
        
        if email:
            print(f"Found email: {email.subject}")

asyncio.run(main())
```

## API Reference

### Main Classes

- `TacomailClient`: Synchronous client for Tacomail API
- `AsyncTacomailClient`: Asynchronous client for Tacomail API
- `Email`: Dataclass representing an email message
- `EmailAddress`: Dataclass for email addresses
- `EmailBody`: Dataclass for email content
- `Attachment`: Dataclass for email attachments

### Common Methods

Both sync and async clients provide these methods:

- `get_random_username()`: Generate a random username
- `get_domains()`: Get list of available domains
- `get_random_address()`: Get a complete random email address
- `get_inbox(address, limit=None)`: Get recent emails
- `get_email(address, mail_id)`: Get a specific email
- `get_attachments(address, mail_id)`: Get email attachments
- `download_attachment(address, mail_id, attachment_id)`: Download an attachment
- `delete_email(address, mail_id)`: Delete a specific email
- `delete_inbox(address)`: Delete all emails in an inbox
- `wait_for_email(address, timeout=30, interval=2)`: Wait for new email
- `wait_for_email_filtered(address, filter_fn, timeout=30, interval=2)`: Wait for email matching criteria

## Requirements

- Python ≥ 3.12
- httpx ≥ 0.28.0

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

The test suite uses [Postmark](https://postmarkapp.com/) to send real test emails to the Tacomail addresses. This ensures the library works with actual email delivery.

1. Sign up for a Postmark account
2. Create a `.env` file in the project root with your credentials:

```bash
# .env
POSTMARK_API_KEY=your_postmark_api_key_here
SENDER_EMAIL=your_email_address_here  # The verified sender email in Postmark
```

Then run the tests:

```bash
pytest

# Run linter
ruff check .
```

## Credits

- Tacomail Service: [https://tacomail.de/](https://tacomail.de/)
- Tacomail Repository: [oskar2517/tacomail](https://github.com/oskar2517/tacomail)
- Tacomail API Documentation: [API.md](https://github.com/oskar2517/tacomail/blob/main/docs/API.md)
