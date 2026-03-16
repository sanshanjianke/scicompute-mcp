import pytest
from unittest.mock import patch, MagicMock
from scicompute_mcp.backends.octave import OctaveBackend
from scicompute_mcp.backends.base import TextContent, ImageContent, ErrorContent


class TestOctaveBackend:
    def test_name_and_capabilities(self):
        backend = OctaveBackend()
        assert backend.name == "octave"
        assert backend.capabilities == ["numeric", "plot"]
    
    def test_is_available_when_not_found(self):
        backend = OctaveBackend()
        with patch("shutil.which", return_value=None):
            assert backend.is_available() is False
    
    def test_is_available_when_found(self):
        backend = OctaveBackend()
        with patch("shutil.which", return_value="/usr/bin/octave"):
            assert backend.is_available() is True
            assert backend._octave_path == "/usr/bin/octave"
    
    def test_start_when_not_available(self):
        backend = OctaveBackend()
        with patch.object(backend, "is_available", return_value=False):
            assert backend.start() is False
    
    def test_start_when_available(self):
        backend = OctaveBackend()
        with patch.object(backend, "is_available", return_value=True):
            assert backend.start() is True
            assert backend._started is True
    
    def test_start_already_started(self):
        backend = OctaveBackend()
        backend._started = True
        assert backend.start() is True
    
    def test_reset(self):
        backend = OctaveBackend()
        backend.reset()
    
    def test_stop(self):
        backend = OctaveBackend()
        backend._started = True
        backend.stop()
        assert backend._started is False
    
    def test_evaluate_not_started(self):
        backend = OctaveBackend()
        with patch.object(backend, "start", return_value=False):
            result = backend.evaluate("1+1")
            assert result.success is False
            assert len(result.content) == 1
            assert result.content[0].message == "Octave not available"