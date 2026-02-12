import { describe, it, expect, beforeEach, vi } from 'vitest';
import { InputHandler } from '../js/input.js';

describe('InputHandler', () => {
  let inputHandler;
  let mockWsClient;
  
  beforeEach(() => {
    mockWsClient = {
      sendInput: vi.fn()
    };
    inputHandler = new InputHandler(mockWsClient);
  });
  
  it('should initialize with no keys pressed', () => {
    expect(inputHandler.keys.ArrowUp).toBeFalsy();
    expect(inputHandler.keys.ArrowLeft).toBeFalsy();
    expect(inputHandler.keys.ArrowRight).toBeFalsy();
  });
  
  it('should track key press', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    inputHandler.handleKeyDown(event);
    
    expect(inputHandler.keys.ArrowUp).toBe(true);
    expect(inputHandler.thrusting).toBe(true);
  });
  
  it('should track key release', () => {
    inputHandler.keys.ArrowUp = true;
    inputHandler.thrusting = true;
    
    const event = new KeyboardEvent('keyup', { key: 'ArrowUp' });
    inputHandler.handleKeyUp(event);
    
    expect(inputHandler.keys.ArrowUp).toBe(false);
    expect(inputHandler.thrusting).toBe(false);
  });
  
  it('should send thrust input when ArrowUp pressed', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    inputHandler.handleKeyDown(event);
    
    expect(mockWsClient.sendInput).toHaveBeenCalledWith('thrust');
  });
  
  it('should send left rotation when ArrowLeft pressed', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    inputHandler.handleKeyDown(event);
    
    expect(mockWsClient.sendInput).toHaveBeenCalledWith('rotate_left');
    expect(inputHandler.rotating).toBe('left');
  });
  
  it('should send right rotation when ArrowRight pressed', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
    inputHandler.handleKeyDown(event);
    
    expect(mockWsClient.sendInput).toHaveBeenCalledWith('rotate_right');
    expect(inputHandler.rotating).toBe('right');
  });
  
  it('should not send duplicate input when key held', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    inputHandler.handleKeyDown(event);
    inputHandler.handleKeyDown(event);
    
    // Should only send once
    expect(mockWsClient.sendInput).toHaveBeenCalledTimes(1);
  });
  
  it('should send thrust_off when ArrowUp released', () => {
    inputHandler.keys.ArrowUp = true;
    const event = new KeyboardEvent('keyup', { key: 'ArrowUp' });
    inputHandler.handleKeyUp(event);
    
    expect(mockWsClient.sendInput).toHaveBeenCalledWith('thrust_off');
  });
  
  it('should clear rotation when arrow keys released', () => {
    inputHandler.rotating = 'left';
    const event = new KeyboardEvent('keyup', { key: 'ArrowLeft' });
    inputHandler.handleKeyUp(event);
    
    expect(inputHandler.rotating).toBeNull();
  });
});
});
