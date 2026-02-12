import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketClient } from '../js/websocket.js';

describe('WebSocketClient - Connection Issues', () => {
  let client;
  
  afterEach(() => {
    if (client) {
      client.close();
    }
  });
  
  it('should close WebSocket connection', () => {
    client = new WebSocketClient('ws://localhost:8000/ws');
    
    // Mock WebSocket
    const mockWs = {
      close: vi.fn(),
      readyState: 1
    };
    
    client.ws = mockWs;
    client.connected = true;
    
    client.close();
    
    // Should call close on WebSocket
    expect(mockWs.close).toHaveBeenCalled();
  });
  
  it('should not send when disconnected', () => {
    client = new WebSocketClient('ws://localhost:8000/ws');
    client.connected = false;
    client.ws = null;
    
    // Should not throw
    expect(() => {
      client.sendInput('thrust');
    }).not.toThrow();
  });
  
  it('should handle message types correctly', () => {
    client = new WebSocketClient('ws://localhost:8000/ws');
    
    const initHandler = vi.fn();
    const telemetryHandler = vi.fn();
    const gameOverHandler = vi.fn();
    
    client.onInit = initHandler;
    client.onTelemetry = telemetryHandler;
    client.onGameOver = gameOverHandler;
    
    // Test init message
    client.handleMessage({ type: 'init', terrain: {}, lander: {} });
    expect(initHandler).toHaveBeenCalled();
    
    // Test telemetry message
    client.handleMessage({ type: 'telemetry', lander: {}, altitude: 100, speed: 2.0, thrusting: true });
    expect(telemetryHandler).toHaveBeenCalled();
    
    // Test game over message
    client.handleMessage({ type: 'game_over', landed: true });
    expect(gameOverHandler).toHaveBeenCalled();
  });
});

describe('WebSocketClient - Spectator Black Screen Bug', () => {
  it('should receive init message with terrain and lander', () => {
    const client = new WebSocketClient('ws://localhost:8000/spectate/test-id');
    
    const initHandler = vi.fn();
    client.onInit = initHandler;
    
    // Simulate receiving init message (this was missing, causing black screen)
    const initMessage = {
      type: 'init',
      terrain: { points: [[0, 700], [1200, 700]] },
      lander: { x: 600, y: 100, vx: 0, vy: 0, rotation: 0, fuel: 1000 }
    };
    
    client.handleMessage(initMessage);
    
    expect(initHandler).toHaveBeenCalledWith(initMessage);
  });
  
  it('should receive telemetry with thrusting state', () => {
    const client = new WebSocketClient('ws://localhost:8000/spectate/test-id');
    
    const telemetryHandler = vi.fn();
    client.onTelemetry = telemetryHandler;
    
    // Telemetry should include thrusting state (was missing, no flame animation)
    const telemetryMessage = {
      type: 'telemetry',
      lander: { x: 600, y: 100, vx: 0, vy: 2, rotation: 0, fuel: 950 },
      altitude: 600,
      speed: 2.0,
      thrusting: true  // This was missing initially
    };
    
    client.handleMessage(telemetryMessage);
    
    expect(telemetryHandler).toHaveBeenCalledWith(telemetryMessage);
    expect(telemetryMessage.thrusting).toBe(true);
  });
});
