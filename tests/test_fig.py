"""
Tests for fig.py figlet generator script.
Tests both explicit command syntax and implicit backwards compatibility.
"""

import contextlib
import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Set up path for importing fig module
sys.path.insert(0, str(Path(__file__).parent.parent))

import fig


class TestHelpAndList:
    """Test help display and font listing functionality."""

    def test_no_args_shows_help(self, capsys):
        """main() with no args should show help via __doc__."""
        with patch.object(sys, 'argv', ['fig.py']):
            fig.main()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "fig.py <preview|generate|list>" in captured.out
        assert "Environment Variables:" in captured.out

    def test_help_command(self, capsys):
        """main(['help']) should show help via __doc__."""
        with patch.object(sys, 'argv', ['fig.py', 'help']):
            fig.main()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "FIGLET_FONT" in captured.out

    def test_help_flags(self, capsys):
        """main(['-h']) and main(['--help']) should show help."""
        for flag in ["-h", "--help"]:
            with patch.object(sys, 'argv', ['fig.py', flag]):
                fig.main()
            captured = capsys.readouterr()
            assert "Usage:" in captured.out

    def test_list_fonts(self, capsys):
        """main(['list']) should show available fonts."""
        with patch.object(sys, 'argv', ['fig.py', 'list']):
            fig.main()
        captured = capsys.readouterr()
        assert "Available fonts:" in captured.out
        # Should contain some common fonts
        assert any(font in captured.out for font in ["standard", "larry3d", "slant"])


class TestPreviewCommand:
    """Test preview command functionality."""

    def test_preview_default(self, capsys):
        """preview() with defaults should generate ASCII art."""
        fig.preview()
        captured = capsys.readouterr()
        # Should generate ASCII art output
        assert len(captured.out.strip()) > 0

    def test_preview_with_font(self, capsys):
        """preview('slant') should use slant font with default text."""
        fig.preview("slant")
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    def test_preview_with_font_and_text(self, capsys):
        """preview('slant', 'Custom') should use both."""
        fig.preview("slant", "Custom")
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    def test_preview_smart_detection_via_main(self, capsys):
        """main(['preview', 'Test']) should treat as text, not font."""
        with patch.object(sys, 'argv', ['fig.py', 'preview', 'Test']):
            fig.main()
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0
        # Should not error about invalid font
        assert "Error:" not in captured.err

    def test_preview_smart_detection_multiword(self, capsys):
        """main(['preview', 'Hello World']) should treat as text."""
        with patch.object(sys, 'argv', ['fig.py', 'preview', 'Hello World']):
            fig.main()
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    def test_preview_invalid_font_fallback(self):
        """Invalid font should fallback to treating as text."""
        # This should not raise an exception
        with (
            patch.object(sys, 'argv', ['fig.py', 'preview', 'nonexistent_font_12345']),
            contextlib.suppress(SystemExit),
        ):
            fig.main()


class TestGenerateCommand:
    """Test generate command functionality."""

    def test_generate_default(self, tmp_path, capsys):
        """generate() should create PNG with defaults."""
        output_file = tmp_path / "test_default.png"
        fig.generate(filename=str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_generate_with_font(self, tmp_path, capsys):
        """generate('slant', 'Test', filename) should use slant font."""
        output_file = tmp_path / "test_font.png"
        fig.generate("slant", "Test Text", str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_generate_with_all_params(self, tmp_path, capsys):
        """generate(font, text, filename) should work."""
        output_file = tmp_path / "test_full.png"
        fig.generate("standard", "Test Text", str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_generate_via_main(self, tmp_path, capsys):
        """main(['generate', font, text, file]) should work."""
        output_file = tmp_path / "test_main.png"
        with patch.object(sys, 'argv', ['fig.py', 'generate', 'standard', 'Test', str(output_file)]):
            fig.main()
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()


class TestImplicitSyntax:
    """Test backwards compatibility with implicit syntax."""

    def test_implicit_text_and_file(self, tmp_path, capsys):
        """main(['text', 'file.png']) should generate with default font."""
        output_file = tmp_path / "implicit_test.png"
        with patch.object(sys, 'argv', ['fig.py', 'Custom Text', str(output_file)]):
            fig.main()
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_implicit_font_text_file(self, tmp_path, capsys):
        """main(['font', 'text', 'file.png']) should generate with specified font."""
        output_file = tmp_path / "implicit_font.png"
        with patch.object(sys, 'argv', ['fig.py', 'slant', 'Test', str(output_file)]):
            fig.main()
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_implicit_file_only(self, tmp_path, capsys):
        """main(['file.png']) should generate with all defaults."""
        output_file = tmp_path / "implicit_defaults.png"
        with patch.object(sys, 'argv', ['fig.py', str(output_file)]):
            fig.main()
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_implicit_font_preview(self, capsys):
        """main(['font']) should preview with font and default text."""
        with patch.object(sys, 'argv', ['fig.py', 'standard']):
            fig.main()
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    def test_implicit_font_text_preview(self, capsys):
        """main(['font', 'text']) should preview with font and text."""
        with patch.object(sys, 'argv', ['fig.py', 'standard', 'Preview Test']):
            fig.main()
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0


class TestEnvironmentVariables:
    """Test environment variable configuration."""

    @patch.dict("os.environ", {"FIGLET_FONT": "slant", "FIGLET_TEXT": "Env Test"})
    def test_env_var_defaults(self, capsys):
        """Environment variables should be used as defaults."""
        fig.preview()
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    @patch.dict("os.environ", {"CANVAS_WIDTH": "500", "CANVAS_HEIGHT": "100"})
    def test_canvas_dimensions_env(self, tmp_path, capsys):
        """Canvas dimensions from env vars should be used."""
        output_file = tmp_path / "env_dimensions.png"
        fig.generate("standard", "Test", str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    @patch.dict("os.environ", {"FONT_COLOR": "red"})
    def test_font_color_env(self, tmp_path, capsys):
        """Font color from env var should be used."""
        output_file = tmp_path / "env_color.png"
        fig.generate("standard", "Test", str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_unexpected_arguments(self, capsys):
        """Unexpected argument patterns should show help."""
        with patch.object(sys, 'argv', ['fig.py', 'invalid', 'too', 'many', 'random', 'args']):
            fig.main()
        captured = capsys.readouterr()
        assert "Unexpected arguments:" in captured.out
        assert "Usage:" in captured.out

    def test_invalid_font_in_generate(self, tmp_path):
        """Invalid font in generate should show error."""
        output_file = tmp_path / "invalid_font.png"
        with pytest.raises(SystemExit):
            fig.generate("invalid_font_12345", "Test", str(output_file))


class TestFileOperations:
    """Test file operations and pathlib integration."""

    def test_png_file_detection(self, tmp_path, capsys):
        """PNG files should be detected regardless of argument order."""
        output_file = tmp_path / "order_test.png"
        with patch.object(sys, 'argv', ['fig.py', 'Test Text', str(output_file)]):
            fig.main()
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()

    def test_absolute_paths(self, tmp_path, capsys):
        """Absolute paths should work correctly."""
        output_file = tmp_path / "absolute.png"
        fig.generate("standard", "Test", str(output_file.absolute()))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()


class TestDirectFunctionCalls:
    """Test calling fig functions directly."""

    def test_list_fonts_direct(self, capsys):
        """list_fonts() should work when called directly."""
        fig.list_fonts()
        captured = capsys.readouterr()
        assert "Available fonts:" in captured.out

    def test_preview_direct(self, capsys):
        """preview() should work when called directly."""
        fig.preview("standard", "Direct Test")
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0

    def test_generate_direct(self, tmp_path, capsys):
        """generate() should work when called directly."""
        output_file = tmp_path / "direct_test.png"
        fig.generate("standard", "Direct Test", str(output_file))
        captured = capsys.readouterr()
        assert "Generated PNG image:" in captured.out
        assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__])
