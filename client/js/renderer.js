export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        this.camera = { x: 0, y: 0 };
    }
    
    clear() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.width, this.height);
    }
    
    drawTerrain(terrain) {
        if (!terrain || !terrain.points) return;
        
        this.ctx.strokeStyle = '#888';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        terrain.points.forEach((point, i) => {
            const x = point[0] - this.camera.x;
            const y = point[1] - this.camera.y;
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        
        this.ctx.stroke();
        
        // Draw landing zones
        if (terrain.landing_zones) {
            this.ctx.strokeStyle = '#0f0';
            this.ctx.lineWidth = 3;
            terrain.landing_zones.forEach(zone => {
                this.ctx.beginPath();
                this.ctx.moveTo(zone.x1 - this.camera.x, zone.y - this.camera.y);
                this.ctx.lineTo(zone.x2 - this.camera.x, zone.y - this.camera.y);
                this.ctx.stroke();
            });
        }
    }
    
    drawLander(lander, thrusting) {
        if (!lander) return;
        
        const x = lander.x - this.camera.x;
        const y = lander.y - this.camera.y;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate(lander.rotation);
        
        // Draw lander body (triangle) - adjusted so bottom is at y position
        this.ctx.fillStyle = lander.crashed ? '#f00' : lander.landed ? '#0f0' : '#fff';
        this.ctx.beginPath();
        this.ctx.moveTo(0, -30);  // Top point
        this.ctx.lineTo(-10, 0);   // Bottom left
        this.ctx.lineTo(10, 0);    // Bottom right
        this.ctx.closePath();
        this.ctx.fill();
        
        // Draw thrust flame
        if (thrusting && lander.fuel > 0) {
            this.ctx.fillStyle = '#ff0';
            this.ctx.beginPath();
            this.ctx.moveTo(-5, 0);
            this.ctx.lineTo(0, 10 + Math.random() * 5);
            this.ctx.lineTo(5, 0);
            this.ctx.closePath();
            this.ctx.fill();
        }
        
        this.ctx.restore();
    }
    
    drawHUD(lander) {
        if (!lander) return;
        
        this.ctx.font = '16px monospace';
        
        // Calculate landing parameters
        const speed = Math.sqrt(lander.vx**2 + lander.vy**2);
        const angle = Math.abs(lander.rotation);
        const angleDegrees = (angle * 180 / Math.PI).toFixed(1);
        
        // Color based on safety thresholds
        // Speed is only dangerous when descending (vy > 0) and too fast
        const speedSafe = lander.vy < 0 || speed < 5.0;  // Updated to 5.0
        const angleSafe = angle < 0.3;
        
        const hud = [
            { label: 'Fuel', value: Math.floor(lander.fuel).toString(), color: lander.fuel > 100 ? '#0f0' : '#f00' },
            { label: 'Altitude', value: Math.floor(this.height - lander.y).toString(), color: '#0f0' },
            { label: 'Speed', value: speed.toFixed(2), color: speedSafe ? '#0f0' : '#f00', target: '< 5.0' },
            { label: 'Angle', value: angleDegrees + '°', color: angleSafe ? '#0f0' : '#f00', target: '< 17°' },
            { label: 'Vertical', value: lander.vy.toFixed(2), color: '#888' },
            { label: 'Horizontal', value: lander.vx.toFixed(2), color: '#888' }
        ];
        
        hud.forEach((item, i) => {
            this.ctx.fillStyle = item.color;
            const text = `${item.label}: ${item.value}`;
            const targetText = item.target ? ` (${item.target})` : '';
            this.ctx.fillText(text + targetText, 10, 30 + i * 20);
        });
        
        // Fuel bar
        const barWidth = 200;
        const barHeight = 20;
        const fuelPercent = lander.fuel / 1000;
        
        this.ctx.strokeStyle = '#0f0';
        this.ctx.strokeRect(10, this.height - 40, barWidth, barHeight);
        this.ctx.fillStyle = fuelPercent > 0.3 ? '#0f0' : '#f00';
        this.ctx.fillRect(10, this.height - 40, barWidth * fuelPercent, barHeight);
    }
    
    updateCamera(lander) {
        if (!lander) return;
        
        // Center camera on lander with some offset
        this.camera.x = lander.x - this.width / 2;
        this.camera.y = lander.y - this.height / 2;
        
        // Clamp camera to terrain bounds
        this.camera.x = Math.max(0, Math.min(this.camera.x, 1200 - this.width));
        this.camera.y = Math.max(0, Math.min(this.camera.y, 800 - this.height));
    }
    
    render(gameState, thrusting) {
        this.clear();
        
        if (gameState.lander) {
            this.updateCamera(gameState.lander);
        }
        
        this.drawTerrain(gameState.terrain);
        this.drawLander(gameState.lander, thrusting);
        this.drawHUD(gameState.lander);
    }
}
