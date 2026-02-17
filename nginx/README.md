# Nginx Setup for Lunar Lander

## Installation

### macOS (Homebrew)
```bash
brew install nginx
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install nginx
```

## Configuration

1. **Copy the config file:**
   ```bash
   # macOS
   cp nginx/lunarlander.conf /opt/homebrew/etc/nginx/servers/
   
   # Linux
   sudo cp nginx/lunarlander.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/lunarlander.conf /etc/nginx/sites-enabled/
   ```

2. **Update the client path in the config:**
   Edit `lunarlander.conf` and change the `root` path to your project location:
   ```nginx
   root /path/to/your/lunarlander/client;
   ```

3. **Test the configuration:**
   ```bash
   # macOS
   nginx -t
   
   # Linux
   sudo nginx -t
   ```

4. **Start/Restart nginx:**
   ```bash
   # macOS
   brew services start nginx
   # or
   brew services restart nginx
   
   # Linux
   sudo systemctl start nginx
   # or
   sudo systemctl restart nginx
   ```

## Verify

Check that nginx is running:
```bash
# macOS
brew services list | grep nginx

# Linux
sudo systemctl status nginx
```

Access the game at: **http://localhost**

## Troubleshooting

- **Port 80 already in use:** Check if another web server is running
- **Permission denied:** On Linux, nginx needs sudo to bind to port 80
- **502 Bad Gateway:** Make sure the Python server is running on port 8000
