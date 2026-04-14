import pytest
from unittest.mock import patch, MagicMock
from scicompute_mcp.backends.octave import OctaveBackend


class TestOctaveBackend:
    def test_name_and_capabilities(self):
        assert OctaveBackend.name == "octave"
        assert OctaveBackend.capabilities == ["numeric", "plot"]
    
    def test_is_available_returns_bool(self):
        result = OctaveBackend.is_available()
        assert isinstance(result, bool)
    
    def test_reset_does_not_raise(self):
        backend = OctaveBackend()
        backend.reset()
    
    def test_stop_does_not_raise(self):
        backend = OctaveBackend()
        backend.stop()
    
    def test_evaluate_not_started_returns_error(self):
        backend = OctaveBackend()
        result = backend.evaluate("1+1")
        assert result.success is False
