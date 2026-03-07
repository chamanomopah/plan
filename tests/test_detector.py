"""
Unit tests for detector.py module.
"""
import pytest
import os
import tempfile
from pathlib import Path
from detector import detect_file_type, get_file_content, get_file_metadata


class TestDetectFileType:
    """Test suite for detect_file_type function."""

    def test_detect_html_by_content(self):
        """Test HTML detection by DOCTYPE."""
        # Create temporary file path
        fd, path = tempfile.mkstemp(suffix='.html')
        try:
            # Write content and close file
            with os.fdopen(fd, 'w') as f:
                f.write('<!DOCTYPE html><html><body>Test</body></html>')

            result = detect_file_type(path)
            assert result["module"] == "html_preview"
            assert result["content_type"] == "text/html"
        finally:
            # Clean up
            if os.path.exists(path):
                os.unlink(path)

    def test_detect_html_by_extension(self):
        """Test HTML detection by file extension."""
        fd, path = tempfile.mkstemp(suffix='.html')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('Some content')

            result = detect_file_type(path)
            assert result["module"] == "html_preview"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_detect_mermaid_by_content(self):
        """Test Mermaid diagram detection."""
        fd, path = tempfile.mkstemp(suffix='.txt')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('graph TD\n    A-->B')

            result = detect_file_type(path)
            assert result["module"] == "meirmaid"
            assert result["content_type"] == "text/mermaid"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_detect_json_file(self):
        """Test JSON file detection by extension."""
        fd, path = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('{"key": "value"}')

            result = detect_file_type(path)
            assert result["module"] == "json_editor"
            assert result["content_type"] == "application/json"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_detect_markdown_file(self):
        """Test Markdown file detection by extension."""
        fd, path = tempfile.mkstemp(suffix='.md')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('# Test Markdown')

            result = detect_file_type(path)
            assert result["module"] == "markdown"
            assert result["content_type"] == "text/markdown"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_detect_image_file(self):
        """Test image file detection by extension."""
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
            fd, path = tempfile.mkstemp(suffix=ext)
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write('fake image content')

                result = detect_file_type(path)
                assert result["module"] == "image_preview"
            finally:
                if os.path.exists(path):
                    os.unlink(path)

    def test_nonexistent_file(self):
        """Test detection of non-existent file."""
        result = detect_file_type("/nonexistent/file.txt")
        assert result["error"] == "File not found"

    def test_empty_file(self):
        """Test detection of empty file."""
        fd, path = tempfile.mkstemp()
        try:
            # Close the file immediately to create an empty file
            os.close(fd)

            result = detect_file_type(path)
            # Empty files should return default text editor
            assert result["module"] == "text_editor"
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestGetFileContent:
    """Test suite for get_file_content function."""

    def test_read_text_file(self):
        """Test reading a text file."""
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write('Test content')

            content = get_file_content(path)
            assert content == 'Test content'
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_read_nonexistent_file(self):
        """Test reading non-existent file returns error."""
        content = get_file_content("/nonexistent/file.txt")
        assert "Error reading file" in content


class TestGetFileMetadata:
    """Test suite for get_file_metadata function."""

    def test_get_existing_file_metadata(self):
        """Test getting metadata for existing file."""
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('Test content')

            metadata = get_file_metadata(path)
            assert metadata["exists"] is True
            assert metadata["size"] > 0
            assert "modified" in metadata
            assert "created" in metadata
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_get_nonexistent_file_metadata(self):
        """Test getting metadata for non-existent file."""
        metadata = get_file_metadata("/nonexistent/file.txt")
        assert metadata["exists"] is False
        assert "error" in metadata
