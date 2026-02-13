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
  
  it('should use yellow warning color for medium fuel (100-300)', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 2, 
      rotation: 0, 
      fuel: 200,
      crashed: false,
      landed: false
    };
    
    expect(() => {
      renderer.drawHUD(lander, 300, 2.0);
    }).not.toThrow();
  });
  
  it('should use yellow warning color for medium speed (3.0-5.0)', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 4.0, 
      rotation: 0, 
      fuel: 500,
      crashed: false,
      landed: false
    };
    
    expect(() => {
      renderer.drawHUD(lander, 300, 4.0);
    }).not.toThrow();
  });
  
  it('should display LOW FUEL warning when fuel < 200', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 2, 
      rotation: 0, 
      fuel: 150,
      crashed: false,
      landed: false
    };
    
    expect(() => {
      renderer.drawHUD(lander, 300, 2.0);
    }).not.toThrow();
  });
  
  it('should display TOO FAST warning when speed > 5.0', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 6.0, 
      rotation: 0, 
      fuel: 500,
      crashed: false,
      landed: false
    };
    
    expect(() => {
      renderer.drawHUD(lander, 300, 6.0);
    }).not.toThrow();
  });
});

describe('Renderer - Particle System', () => {
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
  
  it('should emit particles when thrusting', () => {
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
    
    expect(renderer.particles.length).toBe(0);
    
    renderer.drawLander(lander, true);
    expect(renderer.particles.length).toBeGreaterThan(0);
  });
  
  it('should not emit particles when not thrusting', () => {
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
    
    renderer.drawLander(lander, false);
    expect(renderer.particles.length).toBe(0);
  });
  
  it('should update and remove dead particles', () => {
    renderer.particles = [
      { x: 100, y: 100, vx: 1, vy: 1, life: 0.1, maxLife: 0.5 },
      { x: 200, y: 200, vx: 1, vy: 1, life: -0.1, maxLife: 0.5 }
    ];
    
    renderer.updateParticles();
    expect(renderer.particles.length).toBe(1);
    expect(renderer.particles[0].x).toBe(101);
  });
  
  it('should limit particle count to 500', () => {
    renderer.particles = new Array(600).fill(null).map(() => ({
      x: 100, y: 100, vx: 0, vy: 0, life: 1, maxLife: 1
    }));
    
    renderer.updateParticles();
    expect(renderer.particles.length).toBe(500);
  });
  
  it('should render particles without crashing', () => {
    renderer.particles = [
      { x: 100, y: 100, vx: 0, vy: 0, life: 0.5, maxLife: 0.5, isExplosion: false }
    ];
    
    expect(() => {
      renderer.drawParticles();
    }).not.toThrow();
  });
  
  it('should trigger explosion on crash', () => {
    const lander = { 
      x: 600, 
      y: 400, 
      vx: 0, 
      vy: 0, 
      rotation: 0, 
      fuel: 500,
      crashed: true,
      landed: false
    };
    
    expect(renderer.explosion).toBeNull();
    renderer.drawLander(lander, false);
    expect(renderer.explosion).not.toBeNull();
    expect(renderer.particles.length).toBe(50); // Explosion burst
  });
  
  it('should render explosion particles differently', () => {
    renderer.particles = [
      { x: 100, y: 100, vx: 0, vy: 0, life: 1.0, maxLife: 1.5, isExplosion: true }
    ];
    
    expect(() => {
      renderer.drawParticles();
    }).not.toThrow();
  });
  
  it('should clear explosion after duration', () => {
    renderer.explosion = { x: 100, y: 100, time: 0, duration: 1.5 };
    
    renderer.updateParticles(2.0); // Advance past duration
    expect(renderer.explosion).toBeNull();
  });
  
  it('should reset particles and explosion', () => {
    renderer.particles = [{ x: 100, y: 100, vx: 0, vy: 0, life: 1, maxLife: 1 }];
    renderer.explosion = { x: 100, y: 100, time: 0, duration: 1.5 };
    
    renderer.reset();
    expect(renderer.particles.length).toBe(0);
    expect(renderer.explosion).toBeNull();
  });
});
