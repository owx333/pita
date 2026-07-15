# pita

RFP Module 2 practice quiz website built from the uploaded exam papers.

## What is included

- 75 multiple-choice questions
- Trilingual display: English, Chinese, and Bahasa Melayu
- Instant practice workflow:
  - choose answers
  - check answers
  - view score and per-question correctness
  - optionally show correct answers after checking

## Files

- `index.html` - quiz page
- `mock200.html` - separate 200-question mock exam page
- `styles.css` - page styles
- `app.js` - quiz logic and language switching
- `mock200.js` - logic for the standalone 200-question page
- `data/questions.json` - trilingual question bank + answer key
- `data/questions-data.js` - embedded question bank for direct HTML opening
- `data/mock200.json` - standalone 200-question mock exam bank
- `data/mock200-data.js` - embedded 200-question mock exam bank
- `scripts/build_quiz_data.py` - PDF parser and Malay translation generator
- `scripts/generate_mock200.py` - builds the separate 200-question mock exam from RFP重点

## Regenerate question data

```bash
python3 scripts/build_quiz_data.py \
  --english-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_ENG_d34d.pdf \
  --chinese-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_MAN_be31.pdf \
  --output /workspace/data/questions.json \
  --js-output /workspace/data/questions-data.js
```

If translation service is unavailable, you can still build with English fallback:

```bash
python3 scripts/build_quiz_data.py \
  --english-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_ENG_d34d.pdf \
  --chinese-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_MAN_be31.pdf \
  --output /workspace/data/questions.json \
  --js-output /workspace/data/questions-data.js \
  --skip-translate
```

## Open on Windows (no command needed)

You can directly double-click `index.html` in File Explorer.  
Because `data/questions-data.js` is embedded as JavaScript, the quiz works without a local server.

In `index.html`, use the top **题库 / Question set** selector:

- `75题温习`
- `200题考试`

So you can switch to the 200-question exam mode from the same original page.

## Run locally with server (optional)

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.
