// Environment configuration
const config = {
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000'
        : `${window.location.protocol}//${window.location.host}`,
    WS_PROTOCOL: window.location.protocol === 'https:' ? 'wss:' : 'ws:',
    WS_HOST: window.location.hostname === 'localhost'
        ? 'localhost:8000'
        : window.location.host
};

export default config;
