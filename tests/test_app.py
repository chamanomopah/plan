"""
Unit tests for app.py FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import json
import os

# Import the FastAPI app
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_root_endpoint(self, tmp_path):
        """Test root endpoint returns HTML."""
        # Create a temporary design.html file
        design_file = tmp_path / "design.html"
        design_file.write_text("<html><body>Test Design</body></html>")

        # Save original working directory
        original_cwd = os.getcwd()

        try:
            # Change to temp directory
            os.chdir(tmp_path)

            response = client.get("/")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
        finally:
            os.chdir(original_cwd)

    def test_list_projects_empty(self, tmp_path):
        """Test listing projects when none exist."""
        # Create projetos directory in temp path
        projetos_dir = tmp_path / "projetos"
        projetos_dir.mkdir()

        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/projects")
            assert response.status_code == 200
            assert response.json() == []
        finally:
            os.chdir(original_cwd)

    def test_list_projects_with_config(self, tmp_path):
        """Test listing projects with config.json."""
        # Create project structure
        projetos_dir = tmp_path / "projetos"
        projetos_dir.mkdir()

        project_dir = projetos_dir / "test_project"
        project_dir.mkdir()

        config_file = project_dir / "config.json"
        config_data = {
            "display_name": "Test Project Display",
            "icon": "🧪"
        }
        config_file.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/projects")
            assert response.status_code == 200
            projects = response.json()
            assert len(projects) == 1
            assert projects[0]["name"] == "test_project"
            assert projects[0]["display_name"] == "Test Project Display"
            assert projects[0]["icon"] == "🧪"
        finally:
            os.chdir(original_cwd)

    def test_list_project_files(self, tmp_path):
        """Test listing files in a project."""
        # Create project structure
        projetos_dir = tmp_path / "projetos"
        projetos_dir.mkdir()

        project_dir = projetos_dir / "test_project"
        project_dir.mkdir()

        # Create test files
        (project_dir / "file1.txt").write_text("content1")
        (project_dir / "file2.json").write_text("{}")
        (project_dir / "config.json").write_text('{"display_name": "Test"}')

        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/projects/test_project/files")
            assert response.status_code == 200
            files = response.json()
            # Should exclude config.json
            assert len(files) == 2
            file_names = [f["name"] for f in files]
            assert "file1.txt" in file_names
            assert "file2.json" in file_names
            assert "config.json" not in file_names
        finally:
            os.chdir(original_cwd)

    def test_get_file_content(self, tmp_path):
        """Test getting file content."""
        # Create project structure
        projetos_dir = tmp_path / "projetos"
        projetos_dir.mkdir()

        project_dir = projetos_dir / "test_project"
        project_dir.mkdir()

        test_file = project_dir / "test.txt"
        test_file.write_text("Hello World")

        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/files/test_project/test.txt")
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "Hello World"
            assert data["name"] == "test.txt"
            assert data["project"] == "test_project"
        finally:
            os.chdir(original_cwd)

    def test_get_nonexistent_project(self, tmp_path):
        """Test getting files from non-existent project."""
        projetos_dir = tmp_path / "projetos"
        projetos_dir.mkdir()

        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/projects/nonexistent/files")
            assert response.status_code == 404
        finally:
            os.chdir(original_cwd)

    def test_get_webhooks_config(self, tmp_path):
        """Test getting webhooks configuration."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)
            response = client.get("/api/webhooks/config")
            assert response.status_code == 200
            config = response.json()
            assert "global" in config
            assert "projects" in config
        finally:
            os.chdir(original_cwd)


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Fixture to create temporary directories."""
    return tmp_path_factory.mktemp("test_app")
