# Daily Electricity Consumption

Automated daily notifications of electricity consumption from Caruna Plus.

## Features

- Fetches yesterday's electricity consumption data from Caruna Plus
- Sends daily notifications via ntfy.sh
- Runs automatically every day at 14:00 UTC via GitHub Actions

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
CARUNA_USERNAME=your_username
CARUNA_PASSWORD=your_password
NTFY_TOPIC=your_ntfy_topic
```

3. Run manually:

```bash
python main.py
```

## GitHub Actions

The workflow runs automatically daily. Configure these secrets in your repository:

- `CARUNA_USERNAME`
- `CARUNA_PASSWORD`
- `NTFY_TOPIC`

## Security Notice

**Important:** ntfy.sh topics are public by default. Anyone who knows your topic name can subscribe to it and receive your notifications. Choose a unique, hard-to-guess topic name to minimize the risk.

That said, the notifications only contain daily electricity consumption data (date and kWh usage) — no sensitive personal information, credentials, or other critical data is shared.
