const state = {
  allQuestions: [],
  currentQuestions: [],
  answers: {},
  checked: false,
  showExplanation: false,
};

const els = {
  count: document.querySelector("#mock-count"),
  progress: document.querySelector("#mock-progress"),
  score: document.querySelector("#mock-score"),
  questions: document.querySelector("#mock-questions"),
  tpl: document.querySelector("#mock-question-template"),
  mode200: document.querySelector("#mode-200"),
  mode100: document.querySelector("#mode-100"),
  mode50: document.querySelector("#mode-50"),
  check: document.querySelector("#mock-check"),
  reset: document.querySelector("#mock-reset"),
  showExplanation: document.querySelector("#mock-show-explanation"),
};

function shuffleArray(list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function useQuestionCount(size) {
  if (size >= state.allQuestions.length) {
    state.currentQuestions = [...state.allQuestions];
  } else {
    state.currentQuestions = shuffleArray(state.allQuestions).slice(0, size);
  }
  state.answers = {};
  state.checked = false;
  updateSummary();
  render();
}

function updateSummary() {
  const total = state.currentQuestions.length;
  const answered = Object.keys(state.answers).length;
  els.count.textContent = `当前题量：${total} 题`;
  els.progress.textContent = `已作答 ${answered} / ${total}`;

  if (state.checked) {
    const score = state.currentQuestions.reduce((sum, q) => {
      return state.answers[q.id] === q.answer ? sum + 1 : sum;
    }, 0);
    els.score.textContent = `得分：${score} / ${total}`;
  } else {
    els.score.textContent = "得分：- / -";
  }
}

function makeOption(question, optionKey) {
  const label = document.createElement("label");
  label.className = "option-label";

  const input = document.createElement("input");
  input.type = "radio";
  input.name = `mock-${question.id}`;
  input.value = optionKey;
  input.checked = state.answers[question.id] === optionKey;
  input.addEventListener("change", () => {
    state.answers[question.id] = optionKey;
    state.checked = false;
    updateSummary();
    render();
  });

  const text = document.createElement("span");
  text.textContent = `${optionKey.toUpperCase()}. ${question.options[optionKey]}`;

  label.append(input, text);
  return label;
}

function render() {
  els.questions.textContent = "";
  const ordered = [...state.currentQuestions].sort((a, b) => a.id - b.id);
  ordered.forEach((question, idx) => {
    const node = els.tpl.content.cloneNode(true);
    const number = node.querySelector(".question-number");
    const badge = node.querySelector(".result-badge");
    const chapter = node.querySelector(".chapter-tag");
    const text = node.querySelector(".question-text");
    const optionsWrap = node.querySelector(".options");
    const answerLine = node.querySelector(".answer-line");

    number.textContent = `第 ${idx + 1} 题`;
    chapter.textContent = question.chapter;
    text.textContent = question.question;

    if (!state.checked) {
      badge.textContent = "未批改";
      badge.className = "result-badge";
    } else if (state.answers[question.id] === question.answer) {
      badge.textContent = "正确";
      badge.className = "result-badge correct";
    } else {
      badge.textContent = "错误";
      badge.className = "result-badge wrong";
    }

    ["a", "b", "c", "d"].forEach((key) => {
      const option = makeOption(question, key);
      const input = option.querySelector("input");
      const isSelected = input.checked;
      const isCorrect = key === question.answer;
      if (state.checked && isSelected && !isCorrect) {
        option.classList.add("wrong-highlight");
      }
      if (state.checked && isCorrect) {
        option.classList.add("correct-highlight");
      }
      optionsWrap.append(option);
    });

    answerLine.textContent = `答案：${question.answer.toUpperCase()} | 解析：${question.explanation}`;
    if (state.checked && state.showExplanation) {
      answerLine.classList.remove("hidden");
    } else {
      answerLine.classList.add("hidden");
    }

    els.questions.append(node);
  });
}

function bindEvents() {
  els.mode200.addEventListener("click", () => useQuestionCount(200));
  els.mode100.addEventListener("click", () => useQuestionCount(100));
  els.mode50.addEventListener("click", () => useQuestionCount(50));

  els.check.addEventListener("click", () => {
    state.checked = true;
    updateSummary();
    render();
  });

  els.reset.addEventListener("click", () => {
    state.answers = {};
    state.checked = false;
    updateSummary();
    render();
  });

  els.showExplanation.addEventListener("change", (event) => {
    state.showExplanation = event.target.checked;
    render();
  });
}

function init() {
  const payload = window.__MOCK200_DATA__;
  if (!payload || !Array.isArray(payload.questions)) {
    els.questions.textContent = "题库载入失败。";
    return;
  }
  state.allQuestions = payload.questions;
  bindEvents();
  useQuestionCount(200);
}

init();
