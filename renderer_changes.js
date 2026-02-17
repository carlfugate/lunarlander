// MINIMAL CHANGES FOR MULTIPLE COLORED LANDERS

// 1. Update drawLander method signature and color logic
drawLander(lander, thrusting, playerColor = '#888', playerName = '') {
    if (!lander) return;
    
    // ... existing explosion and particle logic stays the same ...
    
    const x = lander.x - this.camera.x;
    const y = lander.y - this.camera.y;
    
    // ... existing particle emission logic stays the same ...
    
    this.ctx.save();
    this.ctx.translate(x, y);
    this.ctx.rotate(lander.rotation);
    
    const crashed = lander.crashed;
    const landed = lander.landed;
    
    // CHANGE: Use playerColor instead of hardcoded colors
    this.ctx.fillStyle = crashed ? '#f00' : playerColor;
    this.ctx.fillRect(-12, -25, 24, 20);
    
    // CHANGE: Lighter shade of player color for top section
    const lighterColor = this.lightenColor(playerColor, 0.3);
    this.ctx.fillStyle = crashed ? '#f00' : lighterColor;
    this.ctx.fillRect(-8, -30, 16, 5);
    
    // ... windows stay the same ...
    
    // CHANGE: Darker shade of player color for legs
    const darkerColor = this.darkenColor(playerColor, 0.4);
    this.ctx.strokeStyle = crashed ? '#f00' : darkerColor;
    this.ctx.lineWidth = 2;
    
    // ... rest of lander drawing stays the same ...
    
    this.ctx.restore();
    
    // ADD: Draw player name label
    if (playerName) {
        this.ctx.font = 'bold 14px monospace';
        this.ctx.fillStyle = playerColor;
        this.ctx.textAlign = 'center';
        this.ctx.fillText(playerName, x, y - 45);
        this.ctx.textAlign = 'left'; // Reset
    }
}

// 2. Add color utility methods
lightenColor(color, amount) {
    const hex = color.replace('#', '');
    const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + Math.floor(255 * amount));
    const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + Math.floor(255 * amount));
    const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + Math.floor(255 * amount));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

darkenColor(color, amount) {
    const hex = color.replace('#', '');
    const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - Math.floor(255 * amount));
    const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - Math.floor(255 * amount));
    const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - Math.floor(255 * amount));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// 3. Update render method call
render(gameState, thrusting) {
    // ... existing code ...
    
    // CHANGE: Pass color and name when drawing lander
    this.drawLander(gameState.lander, thrusting, gameState.lander?.color, gameState.lander?.name);
    
    // ... rest stays the same ...
}

// 4. For multiple landers, modify render method to handle array
render(gameState, thrusting) {
    this.clear();
    
    if (gameState.landers && gameState.landers.length > 0) {
        // Use first lander for camera
        this.updateCamera(gameState.landers[0]);
    }
    
    this.updateParticles();
    this.drawTerrain(gameState.terrain, gameState.landers?.[0]);
    this.drawParticles();
    
    // CHANGE: Draw all landers
    if (gameState.landers) {
        gameState.landers.forEach(lander => {
            const isThrusting = lander.id === gameState.currentPlayerId ? thrusting : lander.thrusting;
            this.drawLander(lander, isThrusting, lander.color, lander.name);
        });
    }
    
    // Use first lander for HUD
    this.drawHUD(gameState.landers?.[0], gameState.altitude, gameState.speed, gameState.spectatorCount);
}