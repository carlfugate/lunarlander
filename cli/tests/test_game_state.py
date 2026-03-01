import pytest
from game_state import GameState

class TestGameState:
    def test_init(self):
        state = GameState()
        assert state.terrain is None
        assert state.lander is None
        assert state.telemetry is None
        assert state.constants is None
        assert state.game_over is False
        assert state.landed is False
        assert state.crashed is False

    def test_update_from_init(self, sample_game_data):
        state = GameState()
        state.update_from_init(sample_game_data)
        assert state.terrain == sample_game_data['terrain']
        assert state.lander == sample_game_data['lander']
        assert state.constants == sample_game_data['constants']

    def test_update_from_telemetry(self, sample_game_data):
        state = GameState()
        state.update_from_telemetry(sample_game_data)
        assert state.telemetry == sample_game_data
        assert state.lander == sample_game_data['lander']

    def test_update_from_game_over(self):
        state = GameState()
        game_over_data = {'landed': True, 'crashed': False}
        state.update_from_game_over(game_over_data)
        assert state.game_over is True
        assert state.landed is True
        assert state.crashed is False

    def test_get_scaled_terrain(self, sample_game_data):
        state = GameState()
        state.update_from_init(sample_game_data)
        scaled = state.get_scaled_terrain(120, 80)
        assert len(scaled) == 4
        assert scaled[0] == (0, 10)  # (0, 100) scaled down
        assert scaled[1] == (10, 15)  # (100, 150) scaled down

    def test_get_scaled_terrain_no_terrain(self):
        state = GameState()
        scaled = state.get_scaled_terrain(120, 80)
        assert scaled == []

    @pytest.mark.parametrize("rotation,unicode,expected", [
        (0, True, '▲'),
        (1.5, True, '►'),
        (3.5, True, '▼'),
        (-1.5, True, '◄'),
        (0, False, '^'),
        (1.5, False, '>'),
        (3.5, False, 'v'),
        (-1.5, False, '<'),
    ])
    def test_get_lander_char(self, rotation, unicode, expected):
        state = GameState()
        state.lander = {'rotation': rotation}
        assert state.get_lander_char(unicode) == expected

    def test_get_lander_char_no_lander(self):
        state = GameState()
        assert state.get_lander_char() == '^'