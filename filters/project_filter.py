"""Фильтрация заказов по include/exclude словам из конфига."""
from __future__ import annotations

from config.settings import settings
from schemas.project import ProjectDTO


def project_passes_filter(project: ProjectDTO) -> bool:
    """
    Возвращает True, если заказ проходит фильтр:
    - есть хотя бы одно слово из INCLUDE_WORDS в заголовке/описании;
    - нет ни одного слова из EXCLUDE_WORDS.
    """
    haystack = f"{project.title} {project.description}".lower()

    if any(stop_word in haystack for stop_word in settings.exclude_words_list):
        return False

    if not any(inc_word in haystack for inc_word in settings.include_words_list):
        return False

    return True
