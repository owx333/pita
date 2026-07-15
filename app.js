const uiText = {
  en: {
    title: "RFP Module 2 Practice Quiz",
    subtitle: "Trilingual revision website (English / 中文 / Bahasa Melayu)",
    languageLabel: "Language:",
    progressTitle: "Progress",
    answered: (count, total) => `Answered ${count} / ${total}`,
    score: (score, total) => `Score: ${score} / ${total}`,
    scorePending: "Score: - / -",
    checkButton: "Check answers",
    resetButton: "Reset",
    helper: "Tip: You can answer first, then check all at once.",
    questionsTitle: "Questions",
    showAnswer: "Show correct answer after checking",
    questionPrefix: (n) => `Question ${n}`,
    correct: "Correct",
    wrong: "Wrong",
    notChecked: "Not checked",
    correctAnswer: (key, text) => `Correct answer: ${key.toUpperCase()}. ${text}`,
    loading: "Loading questions...",
    loadError: "Failed to load questions data.",
  },
  zh: {
    title: "RFP 第二单元练习测验",
    subtitle: "三语温习网站（英文 / 中文 / 马来文）",
    languageLabel: "语言：",
    progressTitle: "练习进度",
    answered: (count, total) => `已作答 ${count} / ${total}`,
    score: (score, total) => `得分：${score} / ${total}`,
    scorePending: "得分：- / -",
    checkButton: "检查答案",
    resetButton: "重置",
    helper: "提示：可以先全部作答，再一次性批改。",
    questionsTitle: "题目",
    showAnswer: "批改后显示正确答案",
    questionPrefix: (n) => `第 ${n} 题`,
    correct: "正确",
    wrong: "错误",
    notChecked: "未批改",
    correctAnswer: (key, text) => `正确答案：${key.toUpperCase()}. ${text}`,
    loading: "正在载入题目...",
    loadError: "题库载入失败。",
  },
  ms: {
    title: "Kuiz Latihan RFP Modul 2",
    subtitle: "Laman ulang kaji tiga bahasa (English / 中文 / Bahasa Melayu)",
    languageLabel: "Bahasa:",
    progressTitle: "Kemajuan",
    answered: (count, total) => `Dijawab ${count} / ${total}`,
    score: (score, total) => `Skor: ${score} / ${total}`,
    scorePending: "Skor: - / -",
    checkButton: "Semak jawapan",
    resetButton: "Set semula",
    helper: "Tip: Jawab semua dahulu, kemudian semak sekali gus.",
    questionsTitle: "Soalan",
    showAnswer: "Tunjuk jawapan betul selepas semakan",
    questionPrefix: (n) => `Soalan ${n}`,
    correct: "Betul",
    wrong: "Salah",
    notChecked: "Belum disemak",
    correctAnswer: (key, text) => `Jawapan betul: ${key.toUpperCase()}. ${text}`,
    loading: "Memuatkan soalan...",
    loadError: "Gagal memuatkan data soalan.",
  },
};

const state = {
  language: "zh",
  checked: false,
  showCorrectAnswers: false,
  answers: {},
  questions: [],
};

const elements = {
  title: document.querySelector("#app-title"),
  subtitle: document.querySelector("#app-subtitle"),
  languageLabel: document.querySelector("#language-label"),
  languageSelect: document.querySelector("#language-select"),
  summaryTitle: document.querySelector("#summary-title"),
  summaryStatus: document.querySelector("#summary-status"),
  summaryScore: document.querySelector("#summary-score"),
  helper: document.querySelector("#summary-helper"),
  checkButton: document.querySelector("#check-btn"),
  resetButton: document.querySelector("#reset-btn"),
  quizTitle: document.querySelector("#quiz-title"),
  showAnswerLabel: document.querySelector("#show-answer-label"),
  showAnswerToggle: document.querySelector("#show-answer-toggle"),
  questionList: document.querySelector("#question-list"),
  questionTemplate: document.querySelector("#question-template"),
};

function t() {
  return uiText[state.language];
}

function setStaticLabels() {
  const labels = t();
  elements.title.textContent = labels.title;
  elements.subtitle.textContent = labels.subtitle;
  elements.languageLabel.textContent = labels.languageLabel;
  elements.summaryTitle.textContent = labels.progressTitle;
  elements.checkButton.textContent = labels.checkButton;
  elements.resetButton.textContent = labels.resetButton;
  elements.helper.textContent = labels.helper;
  elements.quizTitle.textContent = labels.questionsTitle;
  elements.showAnswerLabel.textContent = labels.showAnswer;
}

function getScore() {
  return state.questions.reduce((score, question) => {
    return state.answers[question.id] === question.answer ? score + 1 : score;
  }, 0);
}

function updateSummary() {
  const labels = t();
  const total = state.questions.length;
  const answeredCount = Object.values(state.answers).filter(Boolean).length;
  elements.summaryStatus.textContent = labels.answered(answeredCount, total);
  elements.summaryScore.textContent = state.checked
    ? labels.score(getScore(), total)
    : labels.scorePending;
}

function createOptionLabel(question, optionKey) {
  const label = document.createElement("label");
  label.className = "option-label";

  const input = document.createElement("input");
  input.type = "radio";
  input.name = `q-${question.id}`;
  input.value = optionKey;
  input.checked = state.answers[question.id] === optionKey;
  input.addEventListener("change", () => {
    state.answers[question.id] = optionKey;
    state.checked = false;
    updateSummary();
    renderQuestions();
  });

  const text = document.createElement("span");
  const optionText = question.options[optionKey][state.language] || "";
  text.textContent = `${optionKey.toUpperCase()}. ${optionText}`;

  label.append(input, text);
  return label;
}

function renderQuestions() {
  elements.questionList.textContent = "";
  const labels = t();

  state.questions.forEach((question) => {
    const fragment = elements.questionTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".question-card");
    const title = fragment.querySelector(".question-number");
    const resultBadge = fragment.querySelector(".result-badge");
    const questionText = fragment.querySelector(".question-text");
    const optionsContainer = fragment.querySelector(".options");
    const answerLine = fragment.querySelector(".answer-line");

    title.textContent = labels.questionPrefix(question.id);
    questionText.textContent = question.question[state.language] || "";

    if (!state.checked) {
      resultBadge.textContent = labels.notChecked;
      resultBadge.className = "result-badge";
    } else if (state.answers[question.id] === question.answer) {
      resultBadge.textContent = labels.correct;
      resultBadge.className = "result-badge correct";
    } else {
      resultBadge.textContent = labels.wrong;
      resultBadge.className = "result-badge wrong";
    }

    ["a", "b", "c", "d"].forEach((optionKey) => {
      const label = createOptionLabel(question, optionKey);
      const input = label.querySelector("input");
      const isSelected = input.checked;
      const isCorrect = question.answer === optionKey;
      if (state.checked && isSelected && !isCorrect) {
        label.classList.add("wrong-highlight");
      }
      if (state.checked && isCorrect) {
        label.classList.add("correct-highlight");
      }
      optionsContainer.append(label);
    });

    const answerText =
      question.options[question.answer]?.[state.language] ||
      question.options[question.answer]?.en ||
      "";
    answerLine.textContent = labels.correctAnswer(question.answer, answerText);
    if (state.checked && state.showCorrectAnswers) {
      answerLine.classList.remove("hidden");
    } else {
      answerLine.classList.add("hidden");
    }

    elements.questionList.append(fragment);
    card?.setAttribute("data-question-id", String(question.id));
  });
}

function wireEvents() {
  elements.languageSelect.addEventListener("change", (event) => {
    state.language = event.target.value;
    setStaticLabels();
    updateSummary();
    renderQuestions();
  });

  elements.checkButton.addEventListener("click", () => {
    state.checked = true;
    updateSummary();
    renderQuestions();
  });

  elements.resetButton.addEventListener("click", () => {
    state.answers = {};
    state.checked = false;
    updateSummary();
    renderQuestions();
  });

  elements.showAnswerToggle.addEventListener("change", (event) => {
    state.showCorrectAnswers = event.target.checked;
    renderQuestions();
  });
}

async function initialize() {
  elements.questionList.textContent = t().loading;
  setStaticLabels();

  try {
    const response = await fetch("./data/questions.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    state.questions = payload.questions || [];
  } catch (error) {
    elements.questionList.textContent = t().loadError;
    console.error(error);
    return;
  }

  wireEvents();
  updateSummary();
  renderQuestions();
}

initialize();
