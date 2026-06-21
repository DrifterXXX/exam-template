# Exam Template Builder

A universal exam preparation website template builder. Generates complete study platforms from structured JSON data with review, practice, and audio support.

## Features

- **Multi-Page Generation** — Builds index, review, practice, and memorize pages
- **JSON Data Source** — Exam content defined in structured JSON format
- **Audio Generation** — Generate TTS audio for study materials
- **Responsive Design** — Mobile-friendly templates with consistent styling
- **Reusable** — Used to build fx-website (期货投资分析) and edu-doctor (教育博士)

## Usage

### 1. Prepare Data

Create exam data following `data_schema.json`:

```json
{
  "title": "考试名称",
  "chapters": [
    {
      "number": 1,
      "title": "章节标题",
      "sections": [...]
    }
  ]
}
```

### 2. Build Website

```bash
python3 build.py --input data.json --output ../output-site/
```

### 3. Generate Audio

```bash
python3 generate_audio.py --input data.json --output ../output-site/audio/
```

## Template Structure

```
template/
├── index.html      # Home page with chapter cards
├── review.html     # Full review content
├── practice.html   # Interactive quiz module
├── memorize.html   # Quick memorization view
├── template.css    # Consistent styling
└── template.js     # Common interactivity
```

## Projects Built With This Template

- [fx-website](https://github.com/DrfterX/fx-website) — 期货投资分析考试备考
- [edu-doctor](https://github.com/DrfterX/edu-doctor) — 教育博士备考

## License

MIT
