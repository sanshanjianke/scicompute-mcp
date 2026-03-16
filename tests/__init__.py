from scicompute_mcp.backends import (
    ComputeBackend,
    Result,
    TextContent,
    ImageContent,
    AudioContent,
    ErrorContent,
    MathematicaBackend,
    OctaveBackend,
)


def test_imports():
    assert ComputeBackend is not None
    assert Result is not None
    assert TextContent is not None
    assert ImageContent is not None
    assert AudioContent is not None
    assert ErrorContent is not None
    assert MathematicaBackend is not None
    assert OctaveBackend is not None


def test_text_content():
    content = TextContent(text="hello")
    assert content.type == "text"
    assert content.text == "hello"


def test_image_content():
    content = ImageContent(data="base64data", mimeType="image/png")
    assert content.type == "image"
    assert content.data == "base64data"
    assert content.mimeType == "image/png"


def test_error_content():
    content = ErrorContent(message="error message")
    assert content.type == "error"
    assert content.message == "error message"


def test_result():
    result = Result(success=True, content=[TextContent(text="ok")])
    assert result.success is True
    assert len(result.content) == 1


def test_mathematica_backend_attributes():
    backend = MathematicaBackend()
    assert backend.name == "mathematica"
    assert "symbolic" in backend.capabilities
    assert "numeric" in backend.capabilities
    assert "plot" in backend.capabilities


def test_octave_backend_attributes():
    backend = OctaveBackend()
    assert backend.name == "octave"
    assert "numeric" in backend.capabilities
    assert "plot" in backend.capabilities