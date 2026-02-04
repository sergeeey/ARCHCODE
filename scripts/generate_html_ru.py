#!/usr/bin/env python3
"""Генерация HTML версии рукописи на русском языке."""

import markdown
from pathlib import Path

MANUSCRIPT_DIR = Path(__file__).parent.parent / "manuscript"
OUTPUT_HTML = Path(__file__).parent.parent / "ARCHCODE_Preprint_RU.html"
FULL_MD = MANUSCRIPT_DIR / "FULL_MANUSCRIPT.md"

CSS = """
<style>
    @page {
        size: A4;
        margin: 2.5cm;
    }

    @media print {
        body { margin: 0; }
        .no-print { display: none; }
    }

    body {
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        max-width: 7.5in;
        margin: 0 auto;
        padding: 40px;
        background: white;
        color: #000;
    }

    h1 {
        font-size: 20pt;
        font-weight: bold;
        margin-top: 24pt;
        margin-bottom: 12pt;
        page-break-after: avoid;
        border-bottom: 2px solid #333;
        padding-bottom: 6pt;
    }

    h2 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 20pt;
        margin-bottom: 10pt;
        page-break-after: avoid;
    }

    h3 {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 14pt;
        margin-bottom: 7pt;
    }

    p {
        text-align: justify;
        margin-bottom: 8pt;
    }

    code {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2px 5px;
        border-radius: 3px;
    }

    pre {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 15px;
        border-left: 4px solid #2196F3;
        overflow-x: auto;
        margin: 12pt 0;
    }

    pre code {
        background: none;
        padding: 0;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15pt 0;
        font-size: 11pt;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8pt;
        text-align: left;
    }

    th {
        background-color: #f0f0f0;
        font-weight: bold;
    }

    blockquote {
        border-left: 4px solid #ccc;
        margin: 12pt 0;
        padding-left: 15pt;
        color: #555;
        font-style: italic;
    }

    em { font-style: italic; }
    strong { font-weight: bold; }

    hr {
        border: none;
        border-top: 1px solid #999;
        margin: 24pt 0;
    }

    .title-page {
        text-align: center;
        margin-bottom: 40pt;
        page-break-after: always;
    }

    .title-page h1 {
        font-size: 22pt;
        margin: 30pt 0 20pt 0;
        border: none;
    }

    .metadata {
        font-size: 11pt;
        color: #666;
        margin: 10pt 0;
    }

    .keywords {
        margin: 20pt 0;
        font-style: italic;
    }

    .print-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2196F3;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 14pt;
        cursor: pointer;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 1000;
    }

    .print-button:hover {
        background: #0b7dda;
    }

    .translation-note {
        background: #fff3cd;
        border: 2px solid #ffc107;
        padding: 20px;
        margin: 20px 0;
        border-radius: 5px;
    }

    .translation-note h3 {
        color: #856404;
        margin-top: 0;
    }
</style>
"""

JS = """
<script>
function printPDF() {
    window.print();
}
</script>
"""

# Русский контент (перевод основных секций)
RUSSIAN_CONTENT = """
<div class="title-page">
<h1>Петля, которая осталась: Физическое моделирование хроматина выявляет слепое пятно ИИ в интерпретации вариантов β-талассемии</h1>

<div class="metadata">
<p><strong>Сергей В. Бойко</strong>¹</p>
<p>¹Независимый исследователь, Алматы, Казахстан</p>
<p><strong>Контакты:</strong> sergeikuch80@gmail.com</p>
<p><strong>Дата:</strong> 4 февраля 2026 года</p>
</div>

<div class="keywords">
<p><strong>Ключевые слова:</strong> β-талассемия, петли хроматина, варианты неопределенной значимости, слепое пятно ИИ, экструзия петель, ARCHCODE</p>
</div>
</div>

<hr>

<div class="translation-note no-print">
<h3>⚠️ Примечание о переводе</h3>
<p><strong>Эта версия содержит переведенные заголовки и метаданные.</strong></p>
<p>Для полного перевода основного текста:</p>
<ol>
<li>Используйте <strong>DeepL.com</strong> (лучшее качество для научных текстов)</li>
<li>Или <strong>ChatGPT</strong>: "Переведи на русский язык следующий научный текст..."</li>
<li>Или любой другой переводчик по выбору</li>
</ol>
<p>Ниже представлен оригинальный английский текст с русскими заголовками секций.</p>
</div>

<h1>Аннотация</h1>

<div class="translation-note">
<p><strong>Раздел требует перевода.</strong> Оригинал в файле: <code>manuscript/ABSTRACT.md</code></p>
<p>Для быстрого перевода: скопируйте текст в DeepL.com</p>
</div>

<h1>Введение</h1>

<h2>Акт I: Кризис вариантов неопределенной значимости — мы живем в золотом веке геномики, но умираем от невежества</h2>

<div class="translation-note">
<p><strong>Раздел требует перевода.</strong> Оригинал в файле: <code>manuscript/INTRODUCTION.md</code></p>
</div>

<h2>Акт II: Революция ИИ обещала спасение, но смотрит в микроскоп, когда нам нужен телескоп</h2>

<h2>Акт III: Проблема интерпретации — когда стабильность структуры становится помехой</h2>

<h2>Акт IV: Наш подход — физика как недостающее звено</h2>

<h1>Методы</h1>

<h2>Симуляция экструзии петель ARCHCODE</h2>

<div class="translation-note">
<p><strong>Раздел требует перевода.</strong> Оригинал в файле: <code>manuscript/METHODS.md</code></p>
<p>Важные термины для сохранения на английском:</p>
<ul>
<li>ARCHCODE, SSIM, AlphaGenome</li>
<li>Kramer kinetics, MED1, CTCF</li>
<li>Loop extrusion, cohesin</li>
</ul>
</div>

<h1>Результаты</h1>

<h2>Открытие "Петли, которая осталась"</h2>

<div class="translation-note">
<p><strong>Раздел требует перевода.</strong> Оригинал в файле: <code>manuscript/RESULTS.md</code></p>
</div>

<h1>Обсуждение</h1>

<h2>Пересматривая парадокс: когда стабильность хроматина становится молекулярной клеткой</h2>

<div class="translation-note">
<p><strong>Раздел требует перевода.</strong> Оригинал в файле: <code>manuscript/DISCUSSION.md</code></p>
</div>

<h2>Слепое пятно ИИ: ортогональные модели для ортогональных механизмов</h2>

<h2>План фальсификации и граничные условия</h2>

<h2>Ограничения и путь к экспериментальной валидации</h2>

<h2>Будущее: ортогональный ИИ и генерация механистических гипотез</h2>

<h1>Литература</h1>

<div class="translation-note">
<p><strong>45 источников в Vancouver формате.</strong> Оригинал в файле: <code>manuscript/REFERENCES.md</code></p>
<p>Литература обычно остается на языке оригинала публикаций.</p>
</div>

<hr>

<div class="no-print">
<h2>Инструкция по созданию полностью переведенной версии</h2>

<h3>Вариант 1: Автоматический перевод (15 минут)</h3>
<ol>
<li>Откройте <strong>DeepL.com</strong></li>
<li>Загрузите файл <code>D:\\ДНК\\manuscript\\FULL_MANUSCRIPT.md</code></li>
<li>Выберите: Английский → Русский</li>
<li>Скачайте переведенный текст</li>
<li>Замените разделы в этом HTML</li>
</ol>

<h3>Вариант 2: Через ChatGPT (20 минут)</h3>
<pre>
Промпт для ChatGPT:
"Переведи на русский язык этот научный текст,
сохраняя термины ARCHCODE, SSIM, AlphaGenome на английском:

[вставь текст секции]"
</pre>

<h3>Вариант 3: Ручной перевод (качественно)</h3>
<p>Переведите каждую секцию вручную для максимального качества научного текста.</p>
</div>
"""

# Читаем английский markdown для справки
if FULL_MD.exists():
    with open(FULL_MD, 'r', encoding='utf-8') as f:
        english_content = f.read()

    # Конвертируем английский контент в HTML для вставки (опционально)
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'sane_lists', 'tables'])
    english_html = md.convert(english_content)
else:
    english_html = "<p>Файл FULL_MANUSCRIPT.md не найден.</p>"

# Полный HTML
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Петля, которая осталась - ARCHCODE Препринт (RU)</title>
    {CSS}
    {JS}
</head>
<body>
    <button class="print-button no-print" onclick="printPDF()">🖨️ Печать в PDF</button>
    {RUSSIAN_CONTENT}

    <div class="no-print" style="margin-top: 50px; padding: 20px; background: #f0f0f0; border-radius: 10px;">
        <h2>📄 Оригинальный английский текст (для справки)</h2>
        <p>Ниже представлен полный текст на английском языке для удобства перевода:</p>
        <hr>
        <div style="opacity: 0.7;">
            {english_html}
        </div>
    </div>
</body>
</html>
"""

# Записываем HTML
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Русская версия HTML создана: {OUTPUT_HTML}")
print(f"📍 Размер: {OUTPUT_HTML.stat().st_size / 1024:.1f} KB")
print(f"\n🚀 Следующие шаги:")
print(f"1. Откройте в браузере: {OUTPUT_HTML}")
print(f"2. Для полного перевода используйте DeepL.com или ChatGPT")
print(f"3. Замените английский текст переведенным")
print(f"4. Нажмите 'Печать в PDF' для создания PDF")
print(f"\n💡 Совет: DeepL.com дает лучшее качество для научных текстов")
