.PHONY: help install install-dev lint test clean format type-check

help:
	@echo "Доступные команды:"
	@echo "  make install      - Установить зависимости проекта"
	@echo "  make install-dev  - Установить зависимости для разработки"
	@echo "  make lint         - Запустить линтер (ruff)"
	@echo "  make format       - Форматировать код (ruff format)"
	@echo "  make type-check   - Проверить типы (mypy)"
	@echo "  make test         - Запустить тесты (pytest)"
	@echo "  make check        - Запустить lint + type-check + test"
	@echo "  make clean        - Очистить временные файлы"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

lint:
	ruff check src tests

format:
	ruff format src tests

type-check:
	mypy src

test:
	pytest

check: lint type-check test
	@echo "Все проверки пройдены успешно!"

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf htmlcov .coverage coverage.xml 2>/dev/null || true











