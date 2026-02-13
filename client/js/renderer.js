export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        this.camera = { x: 0, y: 0 };
        this.particles = [];
        this.explosion = null;
        this.hasExploded = false;
        
        // Make canvas responsive
        this.setupResponsive();
    }
    
    setupResponsive() {
        const resizeCanvas = () => {
            const container = this.canvas.parentElement;
            const scale = Math.min(
                container.clientWidth / 1200,
                container.clientHeight / 800,
                1 // Don't scale up beyond native size
            );
            this.canvas.style.width = (1200 * scale) + 'px';
            this.canvas.style.height = (800 * scale) + 'px';
        };
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
    }
    
    clear() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.width, this.height);
    }
    
    drawTerrain(terrain, lander) {
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
        
        // Draw landing zones with glow
        if (terrain.landing_zones) {
            const pulse = 0.5 + 0.5 * Math.sin(Date.now() / 500);
            
            terrain.landing_zones.forEach(zone => {
                const zoneX = (zone.x1 + zone.x2) / 2;
                const distance = lander ? Math.abs(lander.x - zoneX) : 1000;
                const proximity = Math.max(0, 1 - distance / 500);
                const alpha = 0.3 + 0.4 * pulse + 0.3 * proximity;
                
                // Glow effect
                this.ctx.shadowBlur = 15;
                this.ctx.shadowColor = `rgba(0, 255, 0, ${alpha})`;
                this.ctx.strokeStyle = `rgba(0, 255, 0, ${alpha})`;
                this.ctx.lineWidth = 4;
                
                this.ctx.beginPath();
                this.ctx.moveTo(zone.x1 - this.camera.x, zone.y - this.camera.y);
                this.ctx.lineTo(zone.x2 - this.camera.x, zone.y - this.camera.y);
                this.ctx.stroke();
                
                this.ctx.shadowBlur = 0;
            });
        }
    }
    
    drawLander(lander, thrusting) {
        if (!lander) return;
        
        // Trigger explosion on crash (only once per game)
        if (lander.crashed && !this.hasExploded) {
            this.hasExploded = true;
            this.explosion = {
                x: lander.x,
                y: lander.y,
                time: 0,
                duration: 1.5
            };
            
            // Create explosion particles
            for (let i = 0; i < 50; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = 3 + Math.random() * 5;
                this.particles.push({
                    x: lander.x,
                    y: lander.y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    life: 1.0 + Math.random() * 0.5,
                    maxLife: 1.5,
                    isExplosion: true
                });
            }
        }
        
        // Don't draw lander if exploding
        if (this.explosion && this.explosion.time < 0.5) return;
        
        const x = lander.x - this.camera.x;
        const y = lander.y - this.camera.y;
        
        // Emit particles when thrusting (opposite of thrust direction)
        if (thrusting && lander.fuel > 0 && !lander.crashed) {
            for (let i = 0; i < 3; i++) {
                const spread = (Math.random() - 0.5) * 0.3;
                const speed = 2 + Math.random() * 2;
                // Thrust goes: sin(rot), -cos(rot) [UP]
                // Particles go opposite: -sin(rot), +cos(rot) [DOWN]
                this.particles.push({
                    x: lander.x,
                    y: lander.y,
                    vx: -Math.sin(lander.rotation) * speed + spread,
                    vy: Math.cos(lander.rotation) * speed,
                    life: 0.3,
                    maxLife: 0.3,
                    isExplosion: false
                });
            }
        }
        
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
        
        // Draw thrust flame (shorter)
        if (thrusting && lander.fuel > 0) {
            this.ctx.fillStyle = '#ff0';
            this.ctx.beginPath();
            this.ctx.moveTo(-5, 0);
            this.ctx.lineTo(0, 6 + Math.random() * 3);
            this.ctx.lineTo(5, 0);
            this.ctx.closePath();
            this.ctx.fill();
        }
        
        this.ctx.restore();
    }
    
    updateParticles(dt = 1/60) {
        // Update explosion timer
        if (this.explosion) {
            this.explosion.time += dt;
            if (this.explosion.time > this.explosion.duration) {
                this.explosion = null;
            }
        }
        
        // Update and remove dead particles
        this.particles = this.particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= dt;
            return p.life > 0;
        });
        
        // Limit particle count
        if (this.particles.length > 500) {
            this.particles = this.particles.slice(-500);
        }
    }
    
    drawParticles() {
        this.particles.forEach(p => {
            const alpha = p.life / p.maxLife;
            const size = p.isExplosion ? (3 + alpha * 5) : (2 + alpha * 2);
            
            if (p.isExplosion) {
                // Red/orange/yellow explosion particles
                const hue = 0 + alpha * 60;
                this.ctx.fillStyle = `hsla(${hue}, 100%, 50%, ${alpha})`;
            } else {
                // Orange/yellow thrust particles
                const hue = 30 + alpha * 30;
                this.ctx.fillStyle = `hsla(${hue}, 100%, 50%, ${alpha})`;
            }
            
            this.ctx.fillRect(
                p.x - this.camera.x - size/2,
                p.y - this.camera.y - size/2,
                size,
                size
            );
        });
        
        // Draw explosion flash
        if (this.explosion && this.explosion.time < 0.3) {
            const progress = this.explosion.time / 0.3;
            const radius = 30 + progress * 50;
            const alpha = 1 - progress;
            
            const x = this.explosion.x - this.camera.x;
            const y = this.explosion.y - this.camera.y;
            
            this.ctx.fillStyle = `rgba(255, 200, 0, ${alpha * 0.5})`;
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    drawHUD(lander, altitude, speed, spectatorCount) {
        if (!lander) return;
        
        // Use provided values or calculate fallback
        const displaySpeed = speed !== undefined ? speed : Math.sqrt(lander.vx**2 + lander.vy**2);
        const displayAltitude = altitude !== undefined ? altitude : (this.height - lander.y);
        
        const angle = Math.abs(lander.rotation);
        const angleDegrees = (angle * 180 / Math.PI).toFixed(1);
        
        // Flash effect for critical warnings (2Hz)
        const flash = Math.floor(Date.now() / 250) % 2 === 0;
        
        // Enhanced color coding with yellow warning zone
        const lowFuel = lander.fuel < 200;
        const fuelColor = lander.fuel > 300 ? '#0f0' : lander.fuel > 100 ? '#ff0' : (flash ? '#f00' : '#800');
        
        const highSpeed = displaySpeed > 5.0;
        const speedColor = displaySpeed < 3.0 ? '#0f0' : displaySpeed < 5.0 ? '#ff0' : (flash ? '#f00' : '#800');
        
        const angleColor = angle < 0.2 ? '#0f0' : angle < 0.3 ? '#ff0' : '#f00';
        
        const hud = [
            { label: 'FUEL', value: Math.floor(lander.fuel).toString(), color: fuelColor },
            { label: 'ALT', value: Math.floor(displayAltitude).toString(), color: '#0f0' },
            { label: 'SPEED', value: displaySpeed.toFixed(1), color: speedColor, target: '<5.0' },
            { label: 'ANGLE', value: angleDegrees + '°', color: angleColor, target: '<17°' },
            { label: 'V-VEL', value: lander.vy.toFixed(1), color: '#888' },
            { label: 'H-VEL', value: lander.vx.toFixed(1), color: '#888' }
        ];
        
        // Draw HUD items with background boxes
        this.ctx.font = 'bold 20px monospace';
        hud.forEach((item, i) => {
            const x = 15;
            const y = 25 + i * 35;
            const text = `${item.label}: ${item.value}`;
            const targetText = item.target ? ` (${item.target})` : '';
            const fullText = text + targetText;
            
            // Background box
            const metrics = this.ctx.measureText(fullText);
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(x - 5, y - 18, metrics.width + 10, 26);
            
            // Text
            this.ctx.fillStyle = item.color;
            this.ctx.fillText(fullText, x, y);
        });
        
        // Warning messages (center screen)
        this.ctx.font = 'bold 32px monospace';
        const warnings = [];
        if (lowFuel && flash) warnings.push('⚠ LOW FUEL ⚠');
        if (highSpeed && displayAltitude < 50 && flash) warnings.push('⚠ TOO FAST ⚠');
        
        warnings.forEach((warning, i) => {
            const metrics = this.ctx.measureText(warning);
            const x = (this.width - metrics.width) / 2;
            const y = this.height / 2 - 100 + i * 50;
            
            // Background
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
            this.ctx.fillRect(x - 10, y - 28, metrics.width + 20, 40);
            
            // Text
            this.ctx.fillStyle = '#f00';
            this.ctx.fillText(warning, x, y);
        });
        
        // Spectator count (top right)
        if (spectatorCount !== undefined) {
            this.ctx.font = 'bold 18px monospace';
            const text = `👁 ${spectatorCount} watching`;
            const metrics = this.ctx.measureText(text);
            const x = this.width - metrics.width - 20;
            const y = 30;
            
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(x - 5, y - 18, metrics.width + 10, 26);
            this.ctx.fillStyle = '#888';
            this.ctx.fillText(text, x, y);
        }
        
        // Fuel bar (bottom left)
        const barWidth = 250;
        const barHeight = 25;
        const fuelPercent = lander.fuel / 1000;
        const barX = 15;
        const barY = this.height - 50;
        
        // Background
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(barX - 5, barY - 5, barWidth + 10, barHeight + 10);
        
        // Border
        this.ctx.strokeStyle = '#0f0';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(barX, barY, barWidth, barHeight);
        
        // Fill with color coding
        const barColor = fuelPercent > 0.3 ? '#0f0' : fuelPercent > 0.1 ? '#ff0' : '#f00';
        this.ctx.fillStyle = barColor;
        this.ctx.fillRect(barX, barY, barWidth * fuelPercent, barHeight);
        
        // Label
        this.ctx.font = 'bold 14px monospace';
        this.ctx.fillStyle = '#fff';
        this.ctx.fillText('FUEL', barX + 5, barY - 10);
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
    
    reset() {
        this.particles = [];
        this.explosion = null;
        this.hasExploded = false;
    }
    
    render(gameState, thrusting) {
        this.clear();
        
        if (gameState.lander) {
            this.updateCamera(gameState.lander);
        }
        
        this.updateParticles();
        
        this.drawTerrain(gameState.terrain, gameState.lander);
        this.drawParticles();
        this.drawLander(gameState.lander, thrusting);
        this.drawHUD(gameState.lander, gameState.altitude, gameState.speed, gameState.spectatorCount);
    }
}
