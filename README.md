# Paper Reading Auto-Processor

An automated tool to upload research papers to [Qianwen Read](https://www.qianwen.com/read), extract summaries, and use GPT-4o-mini to analyze them based on your custom questions.

## Features

- **Automated Upload**: Uploads PDF papers from `./paper` to Qianwen Read.
- **Summary Extraction**: Scrapes the "AI Guide" summary from the reading interface.
- **Custom AI Analysis**: Uses GPT-4o-mini (via OpenAI API) to answer any question about the paper's summary.
- **Flexible Result Export**: Saves results (Title, Summary, Answer) to a custom CSV file.
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

1. **Cookies**: Log in to Qianwen Read, export cookies in JSON format, and save as `auto_read/cookies.json`.
2. **Tokens**: Create `auto_read/tokens.yaml` (or in the root) with your OpenAI API key and base URL. (See `tokens.yaml.example`)

## Usage

Place your PDF files in the `./paper` directory, then run:
```bash
cd auto_read
uv run auto_read.py --question "Your custom question here" --output "results.csv"
```

### Example
```bash
uv run auto_read.py --question "Is this a multi-domain rubric benchmark? Answer Yes/No and give reason." --output "answer.csv"
```

## Project Structure

```text
.
├── paper/               # Put your PDFs here
├── auto_read/
│   ├── auto_read.py     # Main script
│   ├── cookies.json     # User cookies
│   ├── tokens.yaml      # API tokens
│   └── chat_screenshots/# Snapshots for verification
└── answer.csv           # Final output (title, summary, answer)
```

## License

MIT License.
