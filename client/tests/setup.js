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
  getImageData: () => ({ data: [0, 0, 0, 255] }),
};

// Mock HTMLCanvasElement
HTMLCanvasElement.prototype.getContext = function() {
  return mockContext;
};

