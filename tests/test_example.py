"""Пример теста для проверки работоспособности pytest."""


def test_example():
    """Базовый тест для проверки настройки pytest."""
    assert True


def test_import():
    """Проверка импорта основного модуля."""
    import src  # noqa: F401
    assert True

