import pytest
from unittest.mock import patch, MagicMock
from scicompute_mcp.manager import BackendManager
from scicompute_mcp.backends.base import TextContent, ErrorContent


class TestBackendManager:
    def test_init(self):
        manager = BackendManager()
        assert "mathematica" in manager._backends
        assert "octave" in manager._backends
    
    def test_list_available_empty(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=False):
            with patch.object(manager._backends["octave"], "is_available", return_value=False):
                available = manager.list_available()
                assert available == []
    
    def test_list_available_octave(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=False):
            with patch.object(manager._backends["octave"], "is_available", return_value=True):
                available = manager.list_available()
                assert len(available) == 1
                assert available[0]["name"] == "octave"
    
    def test_get_backend(self):
        manager = BackendManager()
        backend = manager.get_backend("mathematica")
        assert backend is not None
        assert backend.name == "mathematica"
    
    def test_get_backend_not_found(self):
        manager = BackendManager()
        backend = manager.get_backend("nonexistent")
        assert backend is None
    
    def test_select_backend_by_name(self):
        manager = BackendManager()
        with patch.object(manager._backends["octave"], "is_available", return_value=True):
            backend, msg = manager.select_backend("octave")
            assert backend is not None
            assert backend.name == "octave"
    
    def test_select_backend_by_name_not_available(self):
        manager = BackendManager()
        with patch.object(manager._backends["octave"], "is_available", return_value=False):
            backend, msg = manager.select_backend("octave")
            assert backend is None
            assert "not available" in msg
    
    def test_select_backend_auto(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=True):
            backend, msg = manager.select_backend()
            assert backend is not None
            assert backend.name == "mathematica"
    
    def test_select_backend_auto_skip_unavailable(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=False):
            with patch.object(manager._backends["octave"], "is_available", return_value=True):
                backend, msg = manager.select_backend()
                assert backend is not None
                assert backend.name == "octave"
    
    def test_select_backend_none_available(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=False):
            with patch.object(manager._backends["octave"], "is_available", return_value=False):
                backend, msg = manager.select_backend()
                assert backend is None
                assert "No available backends" in msg
    
    def test_compute_no_backend(self):
        manager = BackendManager()
        with patch.object(manager._backends["mathematica"], "is_available", return_value=False):
            with patch.object(manager._backends["octave"], "is_available", return_value=False):
                result = manager.compute("1+1")
                assert result.success is False
                assert "No available backends" in result.content[0].message
    
    def test_reset_specific_backend(self):
        manager = BackendManager()
        manager._backends["octave"]._started = True
        result = manager.reset("octave")
        assert result["success"] is True
    
    def test_reset_nonexistent_backend(self):
        manager = BackendManager()
        result = manager.reset("nonexistent")
        assert result["success"] is False