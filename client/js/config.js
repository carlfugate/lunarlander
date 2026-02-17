// Environment configuration
const config = {
    API_URL: `${window.location.protocol}//${window.location.host}`,
    WS_PROTOCOL: window.location.protocol === 'https:' ? 'wss:' : 'ws:',
    WS_HOST: window.location.host
};

export default config;
