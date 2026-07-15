const uiText = {
  en: {
    title: "RFP Module 2 Practice Quiz",
    subtitle75: "Trilingual revision website (English / 中文 / Bahasa Melayu)",
    subtitle200: "Mock exam mode: 200 questions from RFP key topics",
    subtitle200Hard: "Advanced mock exam mode: harder 200-question set",
    subtitle400Tri: "Comprehensive mode: 400 trilingual questions",
    datasetPractice75: "75-question revision",
    datasetMock200: "200-question exam",
    datasetMock200Hard: "200-question advanced exam",
    datasetMock400Tri: "400-question trilingual combined set",
    datasetUnavailable:
      "This set is not loaded. Please update files and reload index.html.",
    datasetHint: (name, total) => `Current set: ${name} (${total} questions)`,
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
    title: "PITA练习测验",
    subtitle75: "三语温习网站（英文 / 中文 / 马来文）",
    subtitle200: "模拟考试模式：200题（RFP重点）",
    subtitle200Hard: "加强版模式：200题（更高难度）",
    subtitle400Tri: "综合模式：400题三语题库",
    datasetPractice75: "75题温习",
    datasetMock200: "200题考试",
    datasetMock200Hard: "200题加强版",
    datasetMock400Tri: "400题三语综合",
    datasetUnavailable: "该题库未载入。请先更新文件后重新打开 index.html。",
    datasetHint: (name, total) => `当前题库：${name}（${total}题）`,
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
    subtitle75: "Laman ulang kaji tiga bahasa (English / 中文 / Bahasa Melayu)",
    subtitle200: "Mod peperiksaan simulasi: 200 soalan berdasarkan topik utama RFP",
    subtitle200Hard: "Mod lanjutan: set 200 soalan tahap lebih sukar",
    subtitle400Tri: "Mod komprehensif: 400 soalan tiga bahasa",
    datasetPractice75: "Ulang kaji 75 soalan",
    datasetMock200: "Peperiksaan 200 soalan",
    datasetMock200Hard: "Peperiksaan lanjutan 200 soalan",
    datasetMock400Tri: "Set gabungan tiga bahasa 400 soalan",
    datasetUnavailable:
      "Set ini belum dimuatkan. Sila kemas kini fail dan buka semula index.html.",
    datasetHint: (name, total) => `Set semasa: ${name} (${total} soalan)`,
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
  dataset: "practice75",
  checked: false,
  showCorrectAnswers: false,
  answers: {},
  questions: [],
  datasets: {
    practice75: [],
    mock200: [],
    mock200Hard: [],
    mock400Tri: [],
  },
};

const elements = {
  title: document.querySelector("#app-title"),
  subtitle: document.querySelector("#app-subtitle"),
  languageLabel: document.querySelector("#language-label"),
  languageSelect: document.querySelector("#language-select"),
  summaryTitle: document.querySelector("#summary-title"),
  datasetHint: document.querySelector("#dataset-hint"),
  datasetButton75: document.querySelector("#dataset-btn-75"),
  datasetButton200: document.querySelector("#dataset-btn-200"),
  datasetButton200Hard: document.querySelector("#dataset-btn-200-hard"),
  datasetButton400Tri: document.querySelector("#dataset-btn-400-tri"),
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
  elements.subtitle.textContent = (
    {
      practice75: labels.subtitle75,
      mock200: labels.subtitle200,
      mock200Hard: labels.subtitle200Hard,
      mock400Tri: labels.subtitle400Tri,
    }[state.dataset] || labels.subtitle75
  );
  elements.datasetButton75.textContent = labels.datasetPractice75;
  elements.datasetButton200.textContent = labels.datasetMock200;
  elements.datasetButton200Hard.textContent = labels.datasetMock200Hard;
  elements.datasetButton400Tri.textContent = labels.datasetMock400Tri;
  elements.languageLabel.textContent = labels.languageLabel;
  elements.summaryTitle.textContent = labels.progressTitle;
  elements.checkButton.textContent = labels.checkButton;
  elements.resetButton.textContent = labels.resetButton;
  elements.helper.textContent = labels.helper;
  elements.quizTitle.textContent = labels.questionsTitle;
  elements.showAnswerLabel.textContent = labels.showAnswer;
}

function datasetNameByKey(datasetKey, labels) {
  if (datasetKey === "mock200") {
    return labels.datasetMock200;
  }
  if (datasetKey === "mock200Hard") {
    return labels.datasetMock200Hard;
  }
  if (datasetKey === "mock400Tri") {
    return labels.datasetMock400Tri;
  }
  return labels.datasetPractice75;
}

function updateDatasetButtons() {
  const active = state.dataset;
  const mapping = [
    [elements.datasetButton75, "practice75"],
    [elements.datasetButton200, "mock200"],
    [elements.datasetButton200Hard, "mock200Hard"],
    [elements.datasetButton400Tri, "mock400Tri"],
  ];
  mapping.forEach(([button, key]) => {
    if (key === active) {
      button.classList.remove("secondary");
    } else {
      button.classList.add("secondary");
    }
  });
}

function normalizePractice75Question(question) {
  return {
    id: question.id,
    chapter: "",
    question: question.question,
    options: question.options,
    answer: question.answer,
  };
}

function normalizeMock200Question(question) {
  const toLangMap = (value) => ({ en: value, zh: value, ms: value });
  return {
    id: question.id,
    chapter: question.chapter || "",
    question: toLangMap(question.question),
    options: {
      a: toLangMap(question.options.a),
      b: toLangMap(question.options.b),
      c: toLangMap(question.options.c),
      d: toLangMap(question.options.d),
    },
    answer: question.answer,
  };
}

function normalizeTrilingualQuestion(question) {
  const ensureLangMap = (value) => {
    if (typeof value === "object" && value !== null) {
      return {
        en: value.en || value.zh || value.ms || "",
        zh: value.zh || value.en || value.ms || "",
        ms: value.ms || value.en || value.zh || "",
      };
    }
    return { en: String(value || ""), zh: String(value || ""), ms: String(value || "") };
  };

  return {
    id: question.id,
    chapter: question.chapter || "",
    question: ensureLangMap(question.question),
    options: {
      a: ensureLangMap(question.options?.a),
      b: ensureLangMap(question.options?.b),
      c: ensureLangMap(question.options?.c),
      d: ensureLangMap(question.options?.d),
    },
    answer: question.answer,
  };
}

function switchDataset(datasetKey) {
  const labels = t();
  const nextQuestions = state.datasets[datasetKey];
  if (!nextQuestions || nextQuestions.length === 0) {
    elements.questionList.textContent = labels.datasetUnavailable;
    elements.datasetHint.textContent = labels.datasetUnavailable;
    return;
  }
  state.dataset = datasetKey;
  state.questions = [...nextQuestions];
  state.answers = {};
  state.checked = false;
  setStaticLabels();
  elements.datasetHint.textContent = labels.datasetHint(
    datasetNameByKey(datasetKey, labels),
    state.questions.length
  );
  updateDatasetButtons();
  updateSummary();
  renderQuestions();
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
    const chapterTag = fragment.querySelector(".question-chapter");
    const questionText = fragment.querySelector(".question-text");
    const optionsContainer = fragment.querySelector(".options");
    const answerLine = fragment.querySelector(".answer-line");

    title.textContent = labels.questionPrefix(question.id);
    questionText.textContent = question.question[state.language] || "";
    const chapterText =
      typeof question.chapter === "object" && question.chapter !== null
        ? question.chapter[state.language] || question.chapter.zh || question.chapter.en || ""
        : question.chapter;
    if (chapterText) {
      chapterTag.textContent = chapterText;
      chapterTag.classList.remove("hidden");
    } else {
      chapterTag.classList.add("hidden");
    }

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
  elements.datasetButton75.addEventListener("click", () => switchDataset("practice75"));
  elements.datasetButton200.addEventListener("click", () => switchDataset("mock200"));
  elements.datasetButton200Hard.addEventListener("click", () =>
    switchDataset("mock200Hard")
  );
  elements.datasetButton400Tri.addEventListener("click", () =>
    switchDataset("mock400Tri")
  );

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
  wireEvents();

  try {
    let practicePayload = window.__QUIZ_DATA__;
    if (!practicePayload) {
      const response = await fetch("./data/questions.json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      practicePayload = await response.json();
    }
    state.datasets.practice75 = (practicePayload.questions || []).map(
      normalizePractice75Question
    );

    let mockPayload = window.__MOCK200_TRI_DATA__;
    if (!mockPayload) {
      try {
        const mockResponse = await fetch("./data/mock200-trilingual.json", {
          cache: "no-store",
        });
        if (mockResponse.ok) {
          mockPayload = await mockResponse.json();
        }
      } catch (error) {
        // Keep silent: offline mode may block fetch.
      }
    }
    if (!mockPayload && window.__MOCK200_DATA__) {
      mockPayload = window.__MOCK200_DATA__;
    }
    state.datasets.mock200 = (mockPayload?.questions || []).map((q) =>
      typeof q.question === "object" ? normalizeTrilingualQuestion(q) : normalizeMock200Question(q)
    );

    let mockHardPayload = window.__MOCK200_HARD_TRI_DATA__;
    if (!mockHardPayload) {
      try {
        const mockHardResponse = await fetch("./data/mock200-hard-trilingual.json", {
          cache: "no-store",
        });
        if (mockHardResponse.ok) {
          mockHardPayload = await mockHardResponse.json();
        }
      } catch (error) {
        // Keep silent: offline mode may block fetch.
      }
    }
    if (!mockHardPayload && window.__MOCK200_HARD_DATA__) {
      mockHardPayload = window.__MOCK200_HARD_DATA__;
    }
    state.datasets.mock200Hard = (mockHardPayload?.questions || []).map((q) =>
      typeof q.question === "object" ? normalizeTrilingualQuestion(q) : normalizeMock200Question(q)
    );

    let mock400Payload = window.__MOCK400_DATA__;
    if (!mock400Payload) {
      try {
        const mock400Response = await fetch("./data/mock400-trilingual.json", {
          cache: "no-store",
        });
        if (mock400Response.ok) {
          mock400Payload = await mock400Response.json();
        }
      } catch (error) {
        // Keep silent: offline mode may block fetch.
      }
    }
    state.datasets.mock400Tri = (mock400Payload?.questions || []).map(
      normalizeTrilingualQuestion
    );
  } catch (error) {
    elements.questionList.textContent = t().loadError;
    console.error(error);
    return;
  }

  if (state.datasets.mock200.length === 0) {
    elements.datasetButton200.disabled = true;
  }
  if (state.datasets.mock200Hard.length === 0) {
    elements.datasetButton200Hard.disabled = true;
  }
  if (state.datasets.mock400Tri.length === 0) {
    elements.datasetButton400Tri.disabled = true;
  }
  setStaticLabels();
  switchDataset("practice75");
}

initialize();
