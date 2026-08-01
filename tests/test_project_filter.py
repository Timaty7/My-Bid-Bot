"""Юнит-тесты фильтра include/exclude слов."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from filters.project_filter import project_passes_filter
from schemas.project import ProjectDTO


def _make_project(title: str, description: str = "") -> ProjectDTO:
    return ProjectDTO(
        external_id="123",
        title=title,
        description=description,
        url="https://freelancer.com/projects/123",
    )


@patch("filters.project_filter.settings")
def test_project_passes_with_include_word(mock_settings) -> None:
    mock_settings.include_words_list = ["python", "bot"]
    mock_settings.exclude_words_list = ["wordpress", "php"]

    project = _make_project("Need a Python scraping bot")
    assert project_passes_filter(project) is True


@patch("filters.project_filter.settings")
def test_project_rejected_by_exclude_word(mock_settings) -> None:
    mock_settings.include_words_list = ["python"]
    mock_settings.exclude_words_list = ["wordpress"]

    project = _make_project("Python developer needed for Wordpress plugin")
    assert project_passes_filter(project) is False


@patch("filters.project_filter.settings")
def test_project_rejected_without_include_word(mock_settings) -> None:
    mock_settings.include_words_list = ["python"]
    mock_settings.exclude_words_list = ["wordpress"]

    project = _make_project("Need a Java backend developer")
    assert project_passes_filter(project) is False
