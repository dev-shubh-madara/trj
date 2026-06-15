# GuardBot — Telegram Group Protection Bot

## Overview
A powerful Telegram group protection bot built with Pyrogram. GuardBot protects your group from rule violations, slang, illegal content, and unauthorized changes to group settings.

## Features
- **Certified Members** — Owner can certify trusted members via `/giveaura`; certified users are exempt from all rules and get admin status
- **Media Auto-Delete** — Automatically deletes photos, videos, stickers, files, and GIFs from non-certified members after a configurable delay (10/20/30 seconds)
- **Slang & Illegal Word Filter** — Instantly detects and removes messages containing banned words in any language (Hindi, English, and more)
- **Group Name Protection** — Prevents unauthorized users from changing the group name; bot automatically restores the original name
- **Group Photo Protection** — Prevents unauthorized users from changing/removing the group photo; bot restores the original photo
- **User Authorization** — Owner must authorize users with `/auth <id>` before they can use the bot

## Configuration

### Required Environment Variables
Set these in Replit Secrets:
- `API_ID` — From [my.telegram.org](https://my.telegram.org)
- `API_HASH` — From [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` — From [@BotFather](https://t.me/BotFather)
- `OWNER_ID` — Your Telegram user ID

## Bot Commands

### Private (Owner Only)
| Command | Description |
|---------|-------------|
| `/start` | Show welcome message & command list |
| `/auth <user_id>` | Authorize a user to use the bot |
| `/unauth <user_id>` | Remove user authorization |

### Group Commands (Authorized + Admin)
| Command | Description |
|---------|-------------|
| `/giveaura` | Reply to a user to certify them (makes them admin too) |
| `/removeaura` | Reply to a user to revoke their certification |
| `/setgrouppic <10\|20\|30>` | Set media auto-delete timer in seconds |
| `/groupinfo` | Show current group protection settings |
| `/certified` | List all certified members |
| `/snapshotgroup` | Save current group title & photo as protected values |

## Setup

1. Get API credentials from [my.telegram.org](https://my.telegram.org)
2. Create a bot via [@BotFather](https://t.me/BotFather)
3. Set all environment variables in Replit Secrets
4. Run the bot
5. Add the bot to your group and make it **Admin with all permissions**
6. Use `/snapshotgroup` to save the current group title & photo
7. Use `/giveaura` replying to trusted members to certify them

## User Preferences
- Pyrogram with kurigram imported
- Separate files for all configuration and handlers
- Colored inline buttons: 🔵 Primary (blue), ✅ Success (green), 🔴 Danger (red)
