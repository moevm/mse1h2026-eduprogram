from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from argostranslate import package, translate
from langdetect import LangDetectException, detect


@dataclass
class TranslationStats:
    """Статистика перевода"""
    translated_fields_count: int = 0


def is_russian_text(text: str) -> bool:
    """Возвращает True для русского текста, чтобы пропустить избыточный перевод."""
    if not text or not text.strip():
        return True

    # Быстрая проверка: если есть кириллица и нет латиницы — скорее всего русский
    has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", text))
    has_latin = bool(re.search(r"[A-Za-z]", text))
    if has_cyrillic and not has_latin:
        return True

    try:
        lang = detect(text)
        return lang == "ru"
    except LangDetectException:
        return False


def _find_or_install_translation(from_code: str, to_code: str):
    """Находит установленную модель Argos, иначе пытается установить из индекса."""
    installed_languages = translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)
    if from_lang and to_lang:
        translation = from_lang.get_translation(to_lang)
        if translation:
            return translation

    package.update_package_index()
    available_packages = package.get_available_packages()
    pkg = next((p for p in available_packages if p.from_code == from_code and p.to_code == to_code), None)
    if not pkg:
        raise RuntimeError(f"Пакет перевода {from_code}->{to_code} недоступен")

    package.install_from_path(pkg.download())

    installed_languages = translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)
    if not from_lang or not to_lang:
        raise RuntimeError(f"Не удалось загрузить установленный пакет {from_code}->{to_code}")

    translation = from_lang.get_translation(to_lang)
    if not translation:
        raise RuntimeError(f"Не удалось создать переводчик {from_code}->{to_code}")
    return translation


@lru_cache(maxsize=1)
def _available_source_languages_to_ru() -> set[str]:
    """Собирает исходные языки, с которых можно перевести на русский."""
    result: set[str] = set()

    installed_languages = translate.get_installed_languages()
    ru_lang = next((lang for lang in installed_languages if lang.code == "ru"), None)
    if ru_lang:
        for lang in installed_languages:
            if lang.code == "ru":
                continue
            try:
                if lang.get_translation(ru_lang):
                    result.add(lang.code)
            except Exception:
                continue

    package.update_package_index()
    for pkg in package.get_available_packages():
        if pkg.to_code == "ru":
            result.add(pkg.from_code)

    return result


def _detect_source_language(text: str) -> str:
    """Определяет исходный язык с безопасным fallback для коротких латинских текстов."""
    try:
        detected = detect(text)
    except LangDetectException as exc:
        raise RuntimeError("Не удалось определить исходный язык") from exc

    if detected == "ru":
        return detected

    supported_sources = _available_source_languages_to_ru()
    if detected in supported_sources:
        return detected

    # langdetect может классифицировать короткие английские строки как da/nl и т.д.
    has_latin = bool(re.search(r"[A-Za-z]", text))
    if has_latin and "en" in supported_sources:
        return "en"

    raise RuntimeError(f"Пакет перевода {detected}->ru недоступен")


def _translate_single_text_to_ru(text: str, stats: TranslationStats) -> str:
    """Переводит отдельный текст на русский язык."""
    if not text or not text.strip():
        return text

    if is_russian_text(text):
        return text

    source_lang = _detect_source_language(text)

    if source_lang == "ru":
        return text

    translator = _find_or_install_translation(source_lang, "ru")
    translated = translator.translate(text)
    if translated != text:
        stats.translated_fields_count += 1
    return translated


def _translate_list(values: Iterable[str], stats: TranslationStats) -> list[str]:
    """Переводит список строк на русский язык."""
    return [_translate_single_text_to_ru(value, stats) for value in values]


def translate_work_program_values(work_program) -> tuple[object, TranslationStats]:
    """
    Переводит только поля значений на русский язык.
    Ключи JSON и структура схемы остаются без изменений.
    """
    translated = work_program.model_copy(deep=True)
    stats = TranslationStats()

    translated.nameWorkProgram = _translate_single_text_to_ru(translated.nameWorkProgram, stats)
    translated.previousDisciplines = _translate_list(translated.previousDisciplines, stats)

    new_topics = {}
    for topic_name, topic_data in translated.topics.items():
        translated_topic_name = _translate_single_text_to_ru(topic_name, stats)
        topic_data.educationalUnits = _translate_list(topic_data.educationalUnits, stats)
        new_topics[translated_topic_name] = topic_data

    translated.topics = new_topics
    return translated, stats