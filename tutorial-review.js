const data = window.__TUTORIAL_REVIEW_DATA__;

const els = {
  chapterFilter: document.querySelector("#chapter-filter"),
  keywordFilter: document.querySelector("#keyword-filter"),
  applyFilterButton: document.querySelector("#apply-filter-btn"),
  resetFilterButton: document.querySelector("#reset-filter-btn"),
  summary: document.querySelector("#chapter-summary"),
  objectives: document.querySelector("#learning-objectives"),
  chapterContainer: document.querySelector("#chapter-container"),
};

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function parseLegacyExcerpt(excerpt) {
  if (!excerpt) return [];
  let text = String(excerpt).replace(/\.{3,}/g, " ");
  text = text.replace(/(第\s*\d+\s*章\s*[:：])/g, "|||$1");
  text = text.replace(
    /(风险分类|纯风险的类型|应对风险的态度|个人风险|物业风险|法律责任风险|学习目标|年金的分类|保险类型|风险管理流程)/g,
    "|||$1"
  );

  return text
    .split(/(?:\|\|\||[；;。]|(?<!\d)\s{2,})/)
    .map((item) => item.replace(/\s+/g, " ").trim())
    .filter((item) => item.length >= 6)
    .filter((item) => !/^[0-9\s./:,-]+$/.test(item))
    .slice(0, 16);
}

function splitMessyLineToPoints(line) {
  const seed = String(line || "")
    .replace(/[•▪]/g, "\n")
    .replace(/\s[oO]\s/g, "\n")
    .replace(/(风险分类|纯风险的类型|应对风险的态度|风险分析|保险类型|消费者权益|雇主责任)/g, "\n$1")
    .replace(/\s{2,}/g, "\n");

  const chunks = seed
    .split(/[\n；;。]+/)
    .map((item) => item.replace(/\s+/g, " ").trim())
    .filter(Boolean);

  const compact = [];
  for (const chunk of chunks) {
    if (chunk.length <= 88) {
      compact.push(chunk);
      continue;
    }
    const parts = chunk
      .split(/[，,:：]/)
      .map((item) => item.trim())
      .filter((item) => item.length >= 6);
    if (parts.length > 1) {
      compact.push(...parts);
    } else {
      compact.push(chunk.slice(0, 88));
    }
  }
  return compact;
}

function buildSummaryPoints(chapter, fallbackHighlights) {
  const points = [];
  const pushUnique = (value) => {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    if (!text || text.length < 6 || text.length > 96) return;
    if (/^[0-9\s./:,-]+$/.test(text)) return;
    if (!points.includes(text)) points.push(text);
  };

  for (const item of chapter.memoryChecklist || []) {
    pushUnique(`考试重点：${item}`);
  }

  for (const term of chapter.keyTerms || []) {
    pushUnique(`${term.term}：${term.definition}`);
    if (points.length >= 10) break;
  }

  for (const item of fallbackHighlights || []) {
    for (const piece of splitMessyLineToPoints(item)) {
      pushUnique(piece);
      if (points.length >= 14) break;
    }
    if (points.length >= 14) break;
  }

  return points.slice(0, 14);
}

function buildChapterCard(chapter) {
  const rawHighlights =
    Array.isArray(chapter.sourceHighlights) && chapter.sourceHighlights.length > 0
      ? chapter.sourceHighlights
      : parseLegacyExcerpt(chapter.sourceExcerpt);
  const summaryPoints = buildSummaryPoints(chapter, rawHighlights);
  const highlightItems = summaryPoints
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const termItems = chapter.keyTerms
    .map(
      (item) =>
        `<li><strong>${escapeHtml(item.term)}</strong><br /><span>${escapeHtml(item.definition)}</span></li>`
    )
    .join("");
  const checklistItems = chapter.memoryChecklist
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const sourceExcerpt = escapeHtml(chapter.sourceExcerpt || "（暂无摘录）").replaceAll(
    "\n",
    "<br />"
  );

  return `
    <details class="question-card tutorial-card" open>
      <summary class="tutorial-summary">第 ${chapter.id} 章：${escapeHtml(chapter.title)}</summary>
      <h4>重点整理</h4>
      <ul class="review-list">${highlightItems || "<li>（本章暂无可读重点）</li>"}</ul>
      <details class="tutorial-source">
        <summary>查看原文摘录</summary>
        <p class="answer-line tutorial-excerpt">${sourceExcerpt}</p>
      </details>
      <h4>关键术语</h4>
      <ul class="review-list">${termItems || "<li>（本章暂无自动抽取术语）</li>"}</ul>
      <h4>记忆清单</h4>
      <ul class="review-list">${checklistItems || "<li>（本章暂无清单）</li>"}</ul>
    </details>
  `;
}

function matchesKeyword(chapter, keyword) {
  if (!keyword) return true;
  const haystack = [
    chapter.title,
    chapter.sourceExcerpt,
    ...(chapter.memoryChecklist || []),
    ...((chapter.keyTerms || []).flatMap((k) => [k.term, k.definition])),
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(keyword.toLowerCase());
}

function renderChapters() {
  const selected = String(els.chapterFilter.value || "all");
  const keyword = els.keywordFilter.value.trim();
  const chapters = data.chapters.filter((chapter) => {
    const chapterMatch = selected === "all" || String(chapter.id) === selected;
    const keywordMatch = matchesKeyword(chapter, keyword);
    return chapterMatch && keywordMatch;
  });

  if (chapters.length === 0) {
    els.chapterContainer.innerHTML =
      '<article class="question-card"><p class="question-text">找不到符合条件的章节，请调整筛选条件后重试。</p></article>';
  } else {
    els.chapterContainer.innerHTML = chapters.map(buildChapterCard).join("");
  }
  els.summary.textContent = `当前显示 ${chapters.length} / ${data.chapters.length} 章`;
}

function init() {
  if (!data || !Array.isArray(data.chapters)) {
    els.chapterContainer.textContent = "教材数据载入失败。";
    return;
  }

  els.objectives.innerHTML = data.meta.learningObjectives
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  for (const chapter of data.chapters) {
    const option = document.createElement("option");
    option.value = String(chapter.id);
    option.textContent = `第 ${chapter.id} 章：${chapter.title}`;
    els.chapterFilter.append(option);
  }

  els.applyFilterButton.addEventListener("click", renderChapters);
  els.resetFilterButton.addEventListener("click", () => {
    els.chapterFilter.value = "all";
    els.keywordFilter.value = "";
    renderChapters();
  });
  els.chapterFilter.addEventListener("change", renderChapters);
  els.keywordFilter.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      renderChapters();
    }
  });
  renderChapters();
}

init();
