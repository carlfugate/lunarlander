import pytest
import json
from unittest.mock import AsyncMock, patch, Mock
from websocket_client import WebSocketClient

class TestWebSocketClient:
    def test_init(self):
        client = WebSocketClient()
        assert client.uri == "ws://localhost:8000/ws"
        assert client.ws is None
        assert client.mode is None
        assert client.http_base == "http://localhost:8000"

    def test_init_custom_uri(self):
        client = WebSocketClient("ws://example.com:9000/ws")
        assert client.uri == "ws://example.com:9000/ws"
        assert client.http_base == "http://example.com:9000"

    @pytest.mark.asyncio
    async def test_connect(self, mock_websocket):
        mock_connect = AsyncMock(return_value=mock_websocket)
        with patch('websockets.connect', mock_connect):
            client = WebSocketClient()
            await client.connect()
            mock_connect.assert_called_once_with("ws://localhost:8000/ws")
            assert client.ws == mock_websocket

    @pytest.mark.asyncio
    async def test_connect_custom_uri(self, mock_websocket):
        mock_connect = AsyncMock(return_value=mock_websocket)
        with patch('websockets.connect', mock_connect):
            client = WebSocketClient()
            await client.connect("ws://custom.com/ws")
            mock_connect.assert_called_once_with("ws://custom.com/ws")
            assert client.uri == "ws://custom.com/ws"

    @pytest.mark.asyncio
    async def test_start_game(self, mock_websocket):
        client = WebSocketClient()
        client.ws = mock_websocket
        await client.start_game("hard")
        
        expected_message = json.dumps({"type": "start", "difficulty": "hard"})
        mock_websocket.send.assert_called_once_with(expected_message)
        assert client.mode == "play"

    @pytest.mark.asyncio
    async def test_spectate(self, mock_websocket):
        with patch.object(WebSocketClient, 'connect') as mock_connect:
            client = WebSocketClient()
            await client.spectate("session123")
            mock_connect.assert_called_once_with("ws://localhost:8000/spectate/session123")
            assert client.mode == "spectate"

    @pytest.mark.asyncio
    async def test_fetch_games(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=[{"id": 1, "session": "abc"}])
        
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_get)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = WebSocketClient()
            result = await client.fetch_games()
            assert result == [{"id": 1, "session": "abc"}]

    @pytest.mark.asyncio
    async def test_send_input_play_mode(self, mock_websocket):
        client = WebSocketClient()
        client.ws = mock_websocket
        client.mode = "play"
        
        await client.send_input("thrust")
        expected_message = json.dumps({"type": "input", "action": "thrust"})
        mock_websocket.send.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_send_input_spectate_mode(self, mock_websocket):
        client = WebSocketClient()
        client.ws = mock_websocket
        client.mode = "spectate"
        
        await client.send_input("thrust")
        mock_websocket.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_receive_message(self, mock_websocket):
        test_data = {"type": "telemetry", "data": {"x": 100}}
        mock_websocket.recv.return_value = json.dumps(test_data)
        
        client = WebSocketClient()
        client.ws = mock_websocket
        
        result = await client.receive_message()
        assert result == test_data

    @pytest.mark.asyncio
    async def test_close(self, mock_websocket):
        client = WebSocketClient()
        client.ws = mock_websocket
        
        await client.close()
        mock_websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_no_connection(self):
        client = WebSocketClient()
        # Should not raise exception
        await client.close()