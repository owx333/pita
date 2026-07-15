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
- `styles.css` - page styles
- `app.js` - quiz logic and language switching
- `data/questions.json` - trilingual question bank + answer key
- `scripts/build_quiz_data.py` - PDF parser and Malay translation generator

## Regenerate question data

```bash
python3 scripts/build_quiz_data.py \
  --english-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_ENG_d34d.pdf \
  --chinese-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_MAN_be31.pdf \
  --output /workspace/data/questions.json
```

If translation service is unavailable, you can still build with English fallback:

```bash
python3 scripts/build_quiz_data.py \
  --english-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_ENG_d34d.pdf \
  --chinese-pdf /home/ubuntu/.cursor/projects/workspace/uploads/PCM2_PracExam_MAN_be31.pdf \
  --output /workspace/data/questions.json \
  --skip-translate
```

## Run locally

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.
