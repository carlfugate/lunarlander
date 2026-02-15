// Setup for tests
global.WebSocket = class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 0;
  }
  send() {}
  close() {}
};

// Mock canvas context
const mockContext = {
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 0,
  font: '',
  shadowBlur: 0,
  shadowColor: '',
  fillRect: () => {},
  strokeRect: () => {},
  beginPath: () => {},
  moveTo: () => {},
  lineTo: () => {},
  closePath: () => {},
  fill: () => {},
  stroke: () => {},
  save: () => {},
  restore: () => {},
  translate: () => {},
  rotate: () => {},
  fillText: () => {},
  measureText: (text) => ({ width: text.length * 10 }),
  getImageData: () => ({ data: [0, 0, 0, 255] }),
  arc: () => {},
};

// Mock HTMLCanvasElement
HTMLCanvasElement.prototype.getContext = function() {
  return mockContext;
};

