import pytest
from unittest.mock import patch, MagicMock
from scicompute_mcp.manager import BackendManager
from scicompute_mcp.backends.base import TextContent, ErrorContent


class TestBackendManager:
    def test_init(self):
        manager = BackendManager()
        assert "mathematica" in manager._backend_classes
        assert "octave" in manager._backend_classes
        assert "py_scientific" in manager._backend_classes
    
    def test_list_available(self):
        manager = BackendManager()
        available = manager.list_available()
        assert isinstance(available, list)
        for item in available:
            assert "name" in item
            assert "description" in item
            assert "capabilities" in item
    
    def test_select_backend_by_name(self):
        manager = BackendManager()
        backend, msg = manager.select_backend("py_scientific")
        assert backend is not None
        assert backend.name == "py_scientific"
    
    def test_select_backend_by_name_not_available(self):
        manager = BackendManager()
        backend, msg = manager.select_backend("nonexistent")
        assert backend is None
        assert "not available" in msg
    
    def test_select_backend_auto(self):
        manager = BackendManager()
        backend, msg = manager.select_backend()
        assert backend is not None
    
    def test_compute_with_py_scientific(self):
        manager = BackendManager()
        result = manager.compute("1 + 1", backend="py_scientific")
        assert result.success is True
    
    def test_stop_all(self):
        manager = BackendManager()
        result = manager.stop("ALL")
        assert result["success"] is True
    
    def test_stop_nonexistent(self):
        manager = BackendManager()
        result = manager.stop("nonexistent")
        assert result["success"] is False
