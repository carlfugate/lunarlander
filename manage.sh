#!/bin/bash
# Lunar Lander - Development Management Script

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$PROJECT_DIR/server"
CLIENT_DIR="$PROJECT_DIR/client"
NGINX_CONF="$PROJECT_DIR/nginx.conf"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_status() {
    echo -e "${GREEN}=== Lunar Lander Status ===${NC}"
    
    # Check server
    if pgrep -f "uvicorn main:app" > /dev/null; then
        echo -e "✅ Server: ${GREEN}Running${NC} (http://localhost:8000)"
    else
        echo -e "❌ Server: ${RED}Stopped${NC}"
    fi
    
    # Check nginx
    if pgrep nginx > /dev/null; then
        echo -e "✅ Nginx: ${GREEN}Running${NC} (http://localhost)"
    else
        echo -e "❌ Nginx: ${RED}Stopped${NC}"
    fi
    
    # Check client dev server
    if pgrep -f "vite" > /dev/null; then
        echo -e "✅ Client Dev: ${GREEN}Running${NC} (http://localhost:5173)"
    else
        echo -e "⚪ Client Dev: Not running (using nginx)"
    fi
}

start_server() {
    echo -e "${YELLOW}Starting server...${NC}"
    cd "$SERVER_DIR"
    source venv/bin/activate 2>/dev/null || true
    nohup uvicorn main:app --reload > /tmp/lunarlander-server.log 2>&1 &
    echo $! > /tmp/lunarlander-server.pid
    sleep 2
    echo -e "${GREEN}✅ Server started${NC} (PID: $(cat /tmp/lunarlander-server.pid))"
    echo "   Logs: tail -f /tmp/lunarlander-server.log"
}

stop_server() {
    echo -e "${YELLOW}Stopping server...${NC}"
    pkill -f "uvicorn main:app"
    rm -f /tmp/lunarlander-server.pid
    echo -e "${GREEN}✅ Server stopped${NC}"
}

start_nginx() {
    echo -e "${YELLOW}Starting nginx...${NC}"
    sudo nginx -c "$NGINX_CONF"
    echo -e "${GREEN}✅ Nginx started${NC}"
}

stop_nginx() {
    echo -e "${YELLOW}Stopping nginx...${NC}"
    sudo nginx -s stop
    echo -e "${GREEN}✅ Nginx stopped${NC}"
}

reload_nginx() {
    echo -e "${YELLOW}Reloading nginx...${NC}"
    sudo nginx -s reload
    echo -e "${GREEN}✅ Nginx reloaded${NC}"
}

start_all() {
    start_server
    start_nginx
    echo ""
    show_status
}

stop_all() {
    stop_server
    stop_nginx
    echo ""
    show_status
}

restart_all() {
    stop_all
    sleep 1
    start_all
}

show_logs() {
    echo -e "${YELLOW}Server logs (Ctrl+C to exit):${NC}"
    tail -f /tmp/lunarlander-server.log
}

case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    server:start)
        start_server
        ;;
    server:stop)
        stop_server
        ;;
    server:restart)
        stop_server
        sleep 1
        start_server
        ;;
    nginx:start)
        start_nginx
        ;;
    nginx:stop)
        stop_nginx
        ;;
    nginx:reload)
        reload_nginx
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Lunar Lander Management"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  start              Start server + nginx"
        echo "  stop               Stop server + nginx"
        echo "  restart            Restart everything"
        echo "  status             Show status"
        echo ""
        echo "  server:start       Start server only"
        echo "  server:stop        Stop server only"
        echo "  server:restart     Restart server only"
        echo ""
        echo "  nginx:start        Start nginx only"
        echo "  nginx:stop         Stop nginx only"
        echo "  nginx:reload       Reload nginx config"
        echo ""
        echo "  logs               Tail server logs"
        exit 1
        ;;
esac
