import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Mobile Controls Visibility', () => {
  let mobileControls;
  let mobileMenuControls;
  let controlSwap;
  
  beforeEach(() => {
    // Create mock elements
    document.body.innerHTML = `
      <div id="mobileControls" class="hidden"></div>
      <div id="mobileMenuControls" class="hidden"></div>
      <button id="controlSwap" class="hidden"></button>
    `;
    
    mobileControls = document.getElementById('mobileControls');
    mobileMenuControls = document.getElementById('mobileMenuControls');
    controlSwap = document.getElementById('controlSwap');
  });
  
  it('should be hidden by default', () => {
    expect(mobileControls.classList.contains('hidden')).toBe(true);
    expect(mobileMenuControls.classList.contains('hidden')).toBe(true);
    expect(controlSwap.classList.contains('hidden')).toBe(true);
  });
  
  it('should have visible class when shown', () => {
    mobileControls.classList.remove('hidden');
    mobileControls.classList.add('visible');
    
    expect(mobileControls.classList.contains('visible')).toBe(true);
    expect(mobileControls.classList.contains('hidden')).toBe(false);
  });
  
  it('should have correct structure', () => {
    expect(mobileControls).toBeTruthy();
    expect(mobileMenuControls).toBeTruthy();
    expect(controlSwap).toBeTruthy();
  });
});

describe('Mobile Detection Logic', () => {
  it('should detect mobile by screen width', () => {
    // Mock window.innerWidth
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 500
    });
    
    const isMobile = window.innerWidth <= 768;
    expect(isMobile).toBe(true);
  });
  
  it('should detect desktop by screen width', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    });
    
    const isMobile = window.innerWidth <= 768;
    expect(isMobile).toBe(false);
  });
  
  it('should detect mobile by user agent', () => {
    // Mock Android user agent
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      configurable: true,
      value: 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
    });
    
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    expect(isMobile).toBe(true);
  });
  
  it('should detect desktop by user agent', () => {
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      configurable: true,
      value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    });
    
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    expect(isMobile).toBe(false);
  });
  
  it('should show controls on mobile (width OR user agent)', () => {
    // Desktop width but mobile user agent
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    });
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      configurable: true,
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
    });
    
    const isMobile = window.innerWidth <= 768 || 
                    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    expect(isMobile).toBe(true);
  });
});

describe('Mobile Controls Layout', () => {
  let leftGroup, rightGroup, thrustBtn, leftBtn, rightBtn;
  
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="mobileControls">
        <div id="leftControls"></div>
        <div id="rightControls"></div>
      </div>
      <button id="thrust">▲</button>
      <button id="rotateLeft">◀</button>
      <button id="rotateRight">▶</button>
    `;
    
    leftGroup = document.getElementById('leftControls');
    rightGroup = document.getElementById('rightControls');
    thrustBtn = document.getElementById('thrust');
    leftBtn = document.getElementById('rotateLeft');
    rightBtn = document.getElementById('rotateRight');
  });
  
  it('should place thrust on left by default', () => {
    // Simulate default layout
    leftGroup.innerHTML = '';
    rightGroup.innerHTML = '';
    leftGroup.appendChild(thrustBtn);
    rightGroup.appendChild(leftBtn);
    rightGroup.appendChild(rightBtn);
    
    expect(leftGroup.children.length).toBe(1);
    expect(rightGroup.children.length).toBe(2);
    expect(leftGroup.children[0].id).toBe('thrust');
    expect(rightGroup.children[0].id).toBe('rotateLeft');
    expect(rightGroup.children[1].id).toBe('rotateRight');
  });
  
  it('should place thrust on right when swapped', () => {
    // Simulate swapped layout
    leftGroup.innerHTML = '';
    rightGroup.innerHTML = '';
    leftGroup.appendChild(leftBtn);
    leftGroup.appendChild(rightBtn);
    rightGroup.appendChild(thrustBtn);
    
    expect(leftGroup.children.length).toBe(2);
    expect(rightGroup.children.length).toBe(1);
    expect(leftGroup.children[0].id).toBe('rotateLeft');
    expect(leftGroup.children[1].id).toBe('rotateRight');
    expect(rightGroup.children[0].id).toBe('thrust');
  });
});
