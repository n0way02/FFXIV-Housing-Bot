# FFXIV Housing Discord Bot

A Discord bot to monitor and display available housing plots for Final Fantasy XIV (FFXIV) in real time. The bot fetches data from the [PaissaDB API](https://paissadb.zhu.codes) and posts updates to configured Discord channels, with support for filters, lottery phases, and more.

## Features
- Slash command `/housing_check` to search for available houses by data center, world, size, and district.
- Automatic periodic updates to configured channels with available plots.
- Customizable monitoring per channel (world and district).
- Shows lottery phase, number of entries, price, and time remaining for each plot.
- Admin commands to configure, clear, and manage housing channels.

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ffxiv-housing-bot.git
cd ffxiv-housing-bot
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root with your Discord bot token:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

### 5. Run the bot
```bash
python bot.py
```

## Usage

### Main Commands
- `/housing_check data_center:<name> world:<name> [size] [district]`  
  Search for available houses with optional filters.
- `/set_housing_channel channel:<#channel> world:<name> [district]`  
  Configure a channel to receive automatic updates.
- `/clear_houses channel:<#channel>`  
  (Admin only) Delete all messages in the specified channel.
- `/housing_status`  
  (Admin/Manager only) Check the status of the update task.
- `/housing_help`  
  Show usage instructions for the bot.

## Notes
- The bot requires the following permissions: `Read Messages`, `Send Messages`, `Manage Messages` (for clearing channels).
- Do **not** commit your `.env` file or any sensitive data to your repository.
- The bot will only post updates to channels configured with `/set_housing_channel`.

## License
MIT 