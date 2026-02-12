# Exposing Lunar Lander with nginx + ngrok

## Architecture

```
ngrok (https://abc123.ngrok.io) → port 80
  ↓
nginx (port 80)
  ├── / → Static files (client/)
  ├── /games, /replays, /replay/* → FastAPI (port 8000)
  └── /ws, /spectate/* → WebSocket (port 8000)
```

## Setup

### 1. Install nginx (if not installed)

**macOS:**
```bash
brew install nginx
```

**Linux:**
```bash
sudo apt-get install nginx
```

### 2. Configure nginx

Copy the nginx config:
```bash
# macOS
sudo cp nginx.conf /usr/local/etc/nginx/servers/lunarlander.conf

# Linux
sudo cp nginx.conf /etc/nginx/sites-available/lunarlander
sudo ln -s /etc/nginx/sites-available/lunarlander /etc/nginx/sites-enabled/
```

**Edit the config** to set the correct path:
```bash
# macOS
sudo nano /usr/local/etc/nginx/servers/lunarlander.conf

# Linux
sudo nano /etc/nginx/sites-available/lunarlander
```

Change this line:
```nginx
root /path/to/lunarlander/client;
```

To your actual path (e.g., `/Users/yourname/Documents/Github/lunarlander/client`)

### 3. Start services

**Terminal 1 - Start FastAPI:**
```bash
cd server
source ../venv/bin/activate
uvicorn main:app --port 8000
```

**Terminal 2 - Start nginx:**
```bash
# macOS
sudo nginx
# or restart if already running
sudo nginx -s reload

# Linux
sudo systemctl start nginx
# or restart
sudo systemctl restart nginx
```

**Terminal 3 - Start ngrok:**
```bash
ngrok http 80
```

### 4. Access the game

Open the ngrok URL (e.g., `https://abc123.ngrok.io`)

## How It Works

- **nginx** serves static files and proxies API/WebSocket to FastAPI
- **FastAPI** handles game logic on port 8000
- **ngrok** exposes nginx on port 80 to the internet
- **Single URL** for everything

## Configuration Already Done

The `config.js` already detects the environment correctly:
- Uses current domain for API/WebSocket
- No hardcoded ports
- Works with ngrok automatically

## Testing

1. Open ngrok URL in browser
2. Click "Play Game" - should work
3. Open same URL on another device
4. Click "Spectate" - should see the game

## Troubleshooting

**nginx won't start:**
```bash
# Check config syntax
sudo nginx -t

# Check what's using port 80
sudo lsof -i :80
```

**Static files not loading:**
- Check the `root` path in nginx.conf is correct
- Check file permissions: `ls -la /path/to/lunarlander/client`

**API/WebSocket not working:**
- Check FastAPI is running: `curl http://localhost:8000/games`
- Check nginx error logs:
  - macOS: `/usr/local/var/log/nginx/error.log`
  - Linux: `/var/log/nginx/error.log`

**ngrok connection issues:**
- Free tier supports WebSockets
- Use `https://` URL (not `http://`)

## Stop Services

```bash
# Stop nginx
sudo nginx -s stop

# Stop FastAPI
Ctrl+C in terminal

# Stop ngrok
Ctrl+C in terminal
```

## Alternative: Docker Compose (Optional)

For easier deployment, see `docker-compose.yml` (if you want to create one).
