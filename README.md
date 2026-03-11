# Paper Reading Auto-Processor

An automated tool to upload research papers to [Qianwen Read](https://www.qianwen.com/read), extract summaries, and use GPT-4o-mini to judge if they are multi-domain rubric benchmarks.

## Features

- **Automated Upload**: Uploads PDF papers from `./paper` to Qianwen Read.
- **Summary Extraction**: Scrapes the "AI Guide" summary from the reading interface.
- **AI Analysis**: Uses GPT-4o-mini (via OpenAI API) to analyze the summary.
- **Result Export**: Saves results (Title, Summary, Judgment, Reason) to `answer.xlsx`.
- **Visual Verification**: Captures screenshots of the reading interface for audit.

## Installation

1. Install [uv](https://github.com/astral-sh/uv).
2. Install dependencies:
   ```bash
   cd auto_read
   uv sync
   uv run playwright install chromium
   ```

## Configuration

1. **Cookies**: Log in to Qianwen Read, export cookies in JSON format, and save as `auto_read/cookies.json`. (See `cookies.json.example`)
2. **Tokens**: Create `tokens.yaml` in the project root with your OpenAI API key and base URL. (See `tokens.yaml.example`)

## Usage

Place your PDF files in the `./paper` directory, then run:
```bash
cd auto_read
uv run auto_read.py
```

## Project Structure

```text
.
├── paper/               # Put your PDFs here
├── auto_read/
│   ├── auto_read.py     # Main script
│   ├── cookies.json     # User cookies (ignored by git)
│   └── chat_screenshots/# Snapshots for verification
├── tokens.yaml          # API tokens (ignored by git)
└── answer.xlsx          # Final output (ignored by git)
```

## License

MIT License. See [LICENSE](LICENSE) for details.
