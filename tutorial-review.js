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

function buildChapterCard(chapter) {
  const termItems = chapter.keyTerms
    .map(
      (item) =>
        `<li><strong>${escapeHtml(item.term)}</strong><br /><span>${escapeHtml(item.definition)}</span></li>`
    )
    .join("");
  const checklistItems = chapter.memoryChecklist
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  return `
    <details class="question-card tutorial-card" open>
      <summary class="tutorial-summary">第 ${chapter.id} 章：${escapeHtml(chapter.title)}</summary>
      <p class="answer-line"><strong>原文摘录：</strong>${escapeHtml(chapter.sourceExcerpt)}</p>
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
