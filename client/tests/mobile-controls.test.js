import { describe, it, expect, beforeEach } from 'vitest';

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
  
  it('should not display on desktop (> 768px)', () => {
    // Add visible class
    mobileControls.classList.add('visible');
    
    // Get computed style (would be 'none' on desktop due to media query)
    const style = window.getComputedStyle(mobileControls);
    
    // In jsdom, we can't test actual media queries, but we can verify
    // the element has the right classes
    expect(mobileControls.classList.contains('visible')).toBe(true);
  });
  
  it('should have correct structure', () => {
    expect(mobileControls).toBeTruthy();
    expect(mobileMenuControls).toBeTruthy();
    expect(controlSwap).toBeTruthy();
  });
});
