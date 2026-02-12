# Bookey

A CLI for managing your Google Calendar and Tasks from the terminal.

## Prerequisites

- Python 3.10+
- A Google Cloud project with the Calendar and Tasks APIs enabled
- OAuth 2.0 credentials (`credentials.json`) from the Google Cloud Console

## Setting Up Google Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Calendar API** and **Google Tasks API**
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
5. Choose **Desktop app** as the application type
6. Download the credentials file and rename it to `credentials.json`
7. Place it at `~/.config/bookey/credentials.json`

## Installation

```bash
git clone https://github.com/yourusername/Bookey-TUI.git
cd Bookey-TUI
./install.sh
```

The install script will check for Python 3.10+, install `pipx` if needed, and install Bookey globally.

## Usage

### Interactive Menu

Run `bk` with no flags to open the interactive main menu:

```bash
bk
```

This gives you options to add, delete/complete, list, or change login.

### Flags

| Flag | Description |
|------|-------------|
| `bk -a` | Add an event or task |
| `bk -d` | Delete events / complete tasks (multi-select) |
| `bk -l` | List events and tasks |
| `bk --change-login` | Switch to a different Google account |

### Adding Events

- Enter a date or press Enter for today
- Enter start time in 24hr format (`hh:mm`) or `a` for all-day
- Enter end time in 24hr format

### Adding Tasks

- Enter a name and optional due date (`dd/mm/yyyy`)
- Press Enter to skip the due date for undated tasks

### Deleting Events / Completing Tasks

- Use arrow keys to navigate, space to select, Enter to confirm
- Select multiple items at once
- Tasks are grouped into **Overdue** and **Current** sections

## Updating

To update to a newer version after pulling changes:

```bash
pipx install --force .
```

Or re-run `./install.sh`.
