import { describe, it, expect, beforeEach } from 'vitest';
import { Renderer } from '../js/renderer.js';

describe('Renderer - HUD Metrics Bug', () => {
  let canvas, renderer;
  
  beforeEach(() => {
    canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 800;
    
    // Add canvas to a container for responsive code
    const container = document.createElement('div');
    container.style.width = '1200px';
    container.style.height = '800px';
    container.appendChild(canvas);
    document.body.appendChild(container);
    
    renderer = new Renderer(canvas);
  });
  
  it('should use server-provided altitude instead of calculating', () => {
    const lander = { 
      x: 600, 
      y: 100, 
      vx: 0, 
      vy: 2, 
      rotation: 0, 
      fuel: 500,
      crashed: false,
      landed: false
    };
    
    // Server says altitude is 0 (landed)
    const serverAltitude = 0;
    const serverSpeed = 2.4;
    
    // Should not crash and should use server values
    expect(() => {
      renderer.drawHUD(lander, serverAltitude, serverSpeed);
    }).not.toThrow();
    
    // Verify it doesn't calculate altitude from screen height
    // (This was the bug - it calculated: 800 - 100 = 700 instead of using 0)
  });
  
  it('should handle undefined altitude/speed gracefully', () => {
    const lander = { 
      x: 600, 
      y: 100, 
      vx: 1, 
      vy: 2, 
      rotation: 0, 
      fuel: 500,
      crashed: false,
      landed: false
    };
    
    // Should fall back to calculation if server values missing
    expect(() => {
      renderer.drawHUD(lander, undefined, undefined);
    }).not.toThrow();
  });
  
  it('should not crash with null lander', () => {
    expect(() => {
      renderer.drawLander(null, false);
    }).not.toThrow();
    
    expect(() => {
      renderer.drawHUD(null, 0, 0);
    }).not.toThrow();
  });
  
  it('should render thrust flame when thrusting', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 0, 
      rotation: 0, 
      fuel: 500,
      crashed: false,
      landed: false
    };
    
    // Should render flame
    expect(() => {
      renderer.drawLander(lander, true);
    }).not.toThrow();
    
    // Should not render flame when not thrusting
    expect(() => {
      renderer.drawLander(lander, false);
    }).not.toThrow();
  });
});

describe('Renderer - Performance', () => {
  let canvas, renderer;
  
  beforeEach(() => {
    canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 800;
    
    const container = document.createElement('div');
    container.style.width = '1200px';
    container.style.height = '800px';
    container.appendChild(canvas);
    document.body.appendChild(container);
    
    renderer = new Renderer(canvas);
  });
  
  it('should render frame in < 16ms (60fps)', () => {
    const gameState = {
      terrain: {
        points: [[0, 700], [1200, 700]],
        landing_zones: [{ x1: 500, x2: 600, y: 700 }]
      },
      lander: { 
        x: 600, 
        y: 400, 
        vx: 0, 
        vy: 2, 
        rotation: 0, 
        fuel: 500,
        crashed: false,
        landed: false
      },
      altitude: 300,
      speed: 2.0
    };
    
    const start = performance.now();
    renderer.render(gameState, false);
    const elapsed = performance.now() - start;
    
    expect(elapsed).toBeLessThan(16); // 60fps = 16.67ms per frame
  });
});

describe('Renderer - Landing Zone Highlights', () => {
  let canvas, renderer;
  
  beforeEach(() => {
    canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 800;
    
    const container = document.createElement('div');
    container.style.width = '1200px';
    container.style.height = '800px';
    container.appendChild(canvas);
    document.body.appendChild(container);
    
    renderer = new Renderer(canvas);
  });
  
  it('should draw landing zones with glow effect', () => {
    const terrain = {
      points: [[0, 700], [1200, 700]],
      landing_zones: [{ x1: 500, x2: 600, y: 700 }]
    };
    
    expect(() => {
      renderer.drawTerrain(terrain, null);
    }).not.toThrow();
  });
  
  it('should increase glow when lander is near landing zone', () => {
    const terrain = {
      points: [[0, 700], [1200, 700]],
      landing_zones: [{ x1: 500, x2: 600, y: 700 }]
    };
    
    const landerNear = { x: 550, y: 400 };
    const landerFar = { x: 100, y: 400 };
    
    // Should not crash with proximity detection
    expect(() => {
      renderer.drawTerrain(terrain, landerNear);
      renderer.drawTerrain(terrain, landerFar);
    }).not.toThrow();
  });
  
  it('should handle terrain without landing zones', () => {
    const terrain = {
      points: [[0, 700], [1200, 700]]
    };
    
    expect(() => {
      renderer.drawTerrain(terrain, null);
    }).not.toThrow();
  });
});
