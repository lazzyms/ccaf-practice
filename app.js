
/* ====================================================================
   DOMAIN METADATA
   ==================================================================== */
const DOMAINS = {
  d1: { name: "Agentic Architecture & Orchestration", weight: 0.27, short: "Domain 1",
        desc: "Covers how Claude agents reason and act autonomously: the agentic loop lifecycle (stop_reason signals, tool execution, result injection), multi-agent coordinator–subagent patterns (hub-and-spoke, task decomposition, context passing), and safety mechanisms such as prerequisite gates, enforcement hooks, and graceful error recovery. ~27% of exam weight." },
  d2: { name: "Tool Design & MCP Integration", weight: 0.18, short: "Domain 2",
        desc: "Covers designing effective tools for LLM use: writing clear tool descriptions and input schemas, returning structured vs. error responses, choosing built-in tools (Bash, Grep, Glob, Read, Write) vs. custom MCP servers, and integrating external systems via the Model Context Protocol (MCP). ~18% of exam weight." },
  d3: { name: "Claude Code Configuration & Workflows", weight: 0.20, short: "Domain 3",
        desc: "Covers configuring Claude Code for professional development: the CLAUDE.md instruction hierarchy (project, user, subdirectory), slash commands and skills (context modes, frontmatter), path-specific rules, plan vs. direct execution modes, iterative refinement patterns, and CI/CD pipeline integration. ~20% of exam weight." },
  d4: { name: "Prompt Engineering & Structured Output", weight: 0.20, short: "Domain 4",
        desc: "Covers reliable prompt design and output control: explicit evaluation criteria, few-shot examples, structured output via tool-forcing and JSON schemas, validation and retry loops, batch API for throughput, and multi-pass review patterns. ~20% of exam weight." },
  d5: { name: "Context Management & Reliability", weight: 0.15, short: "Domain 5",
        desc: "Covers managing Claude's stateless context across long conversations: context window budgeting, progressive summarization trade-offs, escalation triggers (policy gaps, explicit customer requests, inability to progress), structured error propagation in multi-agent systems, large-codebase exploration strategies, human-in-the-loop review routing, and source provenance tracking. ~15% of exam weight." },
};





/* ====================================================================
   APP LOGIC
   ==================================================================== */
let state = {
  mode: "random",
  domain: null,
  shuffle: true,
  explain: true,
  questions: [],
  idx: 0,
  correct: 0,
  wrong: 0,
  answered: false,
  selectedIdx: null,
  shuffledOpts: null,
  perDomain: {},
  examMode: false,
  examEndTime: null,
  examTimer: null,
};

const $ = (id) => document.getElementById(id);

/* ---------- Utilities ---------- */
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function weightedPickPool(pool, count) {
  // Build weighted pool by exam blueprint
  const byDomain = {};
  for (const q of pool) {
    if (!byDomain[q.domain]) byDomain[q.domain] = [];
    byDomain[q.domain].push(q);
  }
  const out = [];
  const remaining = {};
  for (const d in DOMAINS) {
    remaining[d] = shuffle(byDomain[d] || []);
  }
  for (let i = 0; i < count; i++) {
    // pick domain by weight using cumulative random
    const r = Math.random();
    let acc = 0;
    let chosenDomain = "d1";
    for (const d in DOMAINS) {
      acc += DOMAINS[d].weight;
      if (r <= acc) { chosenDomain = d; break; }
    }
    // refill if empty
    if (remaining[chosenDomain].length === 0) {
      remaining[chosenDomain] = shuffle(byDomain[chosenDomain] || []);
    }
    if (remaining[chosenDomain].length === 0) {
      // fallback to any non-empty
      for (const d in remaining) {
        if (remaining[d].length) { chosenDomain = d; break; }
      }
    }
    const q = remaining[chosenDomain].pop();
    if (q) out.push(q);
  }
  return out;
}

/* ---------- Home view ---------- */
function renderHome() {
  $("homeView").style.display = "";
  $("quizView").style.display = "none";
  $("summaryView").style.display = "none";

  // stats-mini
  const total = window.QUESTION_BANK.length;
  $("statsMini").innerHTML = `<span><b>${total}</b> questions</span><span><b>5</b> domains</span>`;

  // domain stats
  const counts = {};
  for (const q of window.QUESTION_BANK) {
    counts[q.domain] = (counts[q.domain] || 0) + 1;
  }
  const statsHtml = Object.keys(DOMAINS).map(d => {
    const c = counts[d] || 0;
    return `<div class="domain-stat" style="flex-direction:column;align-items:flex-start;gap:3px;padding:10px 0;">
      <div style="display:flex;justify-content:space-between;width:100%;"><span style="font-weight:500;color:var(--text)">${DOMAINS[d].short} — ${DOMAINS[d].name}</span><b style="white-space:nowrap;">${c} q · ${Math.round(DOMAINS[d].weight*100)}%</b></div>
      <div style="font-size:12.5px;color:var(--text-muted);line-height:1.5;">${DOMAINS[d].desc}</div>
    </div>`;
  }).join("");
  $("domainStats").innerHTML = statsHtml;

  // mode cards
  document.querySelectorAll(".mode-card").forEach(card => {
    card.classList.toggle("active", card.dataset.mode === state.mode);
    card.onclick = () => {
      state.mode = card.dataset.mode;
      renderHome();
    };
  });

  // domain picker visibility
  $("domainPicker").classList.toggle("visible", state.mode === "domain");
  if (state.mode === "domain") {
    const dpHtml = Object.keys(DOMAINS).map(d => {
      const c = counts[d] || 0;
      const checked = state.domain === d ? "checked" : "";
      return `<label><input type="radio" name="domain" value="${d}" ${checked}><span>${DOMAINS[d].short} · ${DOMAINS[d].name}</span><span class="domain-meta">${c} q</span></label>`;
    }).join("");
    const selectedDesc = state.domain ? `<div style="margin-top:10px;padding:10px 14px;background:var(--accent-soft);border:1px solid var(--border);border-radius:8px;font-size:13px;color:var(--text-muted);line-height:1.5;" id="domainDescBox">${DOMAINS[state.domain || 'd1'].desc}</div>` : "";
    $("domainPicker").innerHTML = dpHtml + selectedDesc;
    $("domainPicker").querySelectorAll("input").forEach(inp => {
      inp.onchange = () => {
        state.domain = inp.value;
        const box = document.getElementById("domainDescBox");
        if (box) box.textContent = DOMAINS[inp.value].desc;
      };
    });
    if (!state.domain) state.domain = "d1";
    $("domainPicker").querySelector(`input[value="${state.domain}"]`).checked = true;
  }

  $("optShuffle").checked = state.shuffle;
  $("optExplain").checked = state.explain;
  $("optShuffle").onchange = () => state.shuffle = $("optShuffle").checked;
  $("optExplain").onchange = () => state.explain = $("optExplain").checked;

  // disable explain toggle in exam mode (no explanations until end)
  if (state.mode === "exam") {
    $("optExplain").checked = false;
    $("optExplain").disabled = true;
  } else {
    $("optExplain").disabled = false;
  }

  // start button label
  const labels = {
    random: "Start random session →",
    domain: "Start domain drill →",
    exam: "Begin 90-minute exam →",
    quickset: "Start quick 10 →",
  };
  $("startBtn").textContent = labels[state.mode];
  $("startBtn").onclick = startQuiz;
}

/* ---------- Quiz session ---------- */
function startQuiz() {
  let pool = window.QUESTION_BANK;
  let count = 40; // default
  state.examMode = false;
  state.examEndTime = null;

  if (state.mode === "random") {
    state.questions = weightedPickPool(pool, 50);
  } else if (state.mode === "domain") {
    const dp = pool.filter(q => q.domain === state.domain);
    state.questions = shuffle(dp);
  } else if (state.mode === "exam") {
    state.questions = weightedPickPool(pool, 65);
    state.examMode = true;
    state.examEndTime = Date.now() + 90 * 60 * 1000;
    state.explain = false;
  } else if (state.mode === "quickset") {
    state.questions = weightedPickPool(pool, 10);
  }

  state.idx = 0;
  state.correct = 0;
  state.wrong = 0;
  state.answered = false;
  state.selectedIdx = null;
  state.perDomain = {};
  for (const d in DOMAINS) state.perDomain[d] = { right: 0, wrong: 0, total: 0 };

  $("homeView").style.display = "none";
  $("quizView").style.display = "";
  $("summaryView").style.display = "none";

  $("quizExit").onclick = () => {
    if (confirm("Exit this session? Your progress will be lost.")) {
      stopTimer();
      renderHome();
    }
  };

  if (state.examMode) {
    $("quizTimer").style.display = "";
    startTimer();
  } else {
    $("quizTimer").style.display = "none";
  }

  renderQuestion();
}

function startTimer() {
  stopTimer();
  state.examTimer = setInterval(() => {
    const left = Math.max(0, state.examEndTime - Date.now());
    const mins = Math.floor(left / 60000);
    const secs = Math.floor((left % 60000) / 1000);
    $("quizTimer").textContent = `${String(mins).padStart(2,"0")}:${String(secs).padStart(2,"0")}`;
    if (left <= 5 * 60 * 1000) $("quizTimer").classList.add("warning");
    if (left <= 0) {
      stopTimer();
      finishQuiz();
    }
  }, 500);
}
function stopTimer() {
  if (state.examTimer) { clearInterval(state.examTimer); state.examTimer = null; }
}

function renderQuestion() {
  if (state.idx >= state.questions.length) return finishQuiz();
  const q = state.questions[state.idx];

  $("qNum").textContent = state.idx + 1;
  $("qTotal").textContent = state.questions.length;
  $("quizScore").innerHTML = `<span class="right">${state.correct}</span> correct · <span class="wrong">${state.wrong}</span> wrong`;

  // shuffle options
  const optOrder = state.shuffle ? shuffle([0,1,2,3]) : [0,1,2,3];
  state.shuffledOpts = optOrder;
  const correctOriginal = q.correct; // 0..3 in original order
  const correctShuffled = optOrder.indexOf(correctOriginal);

  state.answered = false;
  state.selectedIdx = null;

  const letters = ["A","B","C","D"];
  const optsHtml = optOrder.map((origIdx, i) => `
    <button class="option" data-idx="${i}" data-orig="${origIdx}" data-correct="${i === correctShuffled ? 1 : 0}">
      <span class="option-letter">${letters[i]}</span>
      <span class="option-text">${q.options[origIdx]}</span>
    </button>
  `).join("");

  const scenarioHtml = q.scenario
    ? `<div class="scenario-box"><div class="scenario-label">Scenario</div>${q.scenario}</div>`
    : "";

  const html = `
    <div class="question-card">
      <div class="question-domain">${DOMAINS[q.domain].short} · ${q.task || ""}</div>
      ${scenarioHtml}
      <div class="question-text">${q.question}</div>
      <div class="options" id="optsContainer">${optsHtml}</div>
      <div id="verdictContainer"></div>
    </div>
    <div class="actions">
      <div class="actions-left">
        <button class="start-btn secondary" id="exitMid">Exit to home</button>
      </div>
      <div class="actions-right">
        <button class="start-btn" id="submitBtn" disabled>Submit answer</button>
        <button class="start-btn" id="nextBtn" style="display:none;">Next question →</button>
      </div>
    </div>
  `;
  $("questionContainer").innerHTML = html;

  // wire option clicks
  document.querySelectorAll(".option").forEach(opt => {
    opt.onclick = () => {
      if (state.answered) return;
      document.querySelectorAll(".option").forEach(o => o.classList.remove("selected"));
      opt.classList.add("selected");
      state.selectedIdx = parseInt(opt.dataset.idx);
      $("submitBtn").disabled = false;
    };
  });

  $("submitBtn").onclick = () => submitAnswer(q, correctShuffled);
  $("nextBtn").onclick = () => { state.idx++; renderQuestion(); };
  $("exitMid").onclick = () => {
    if (confirm("Exit this session? Your progress will be lost.")) {
      stopTimer();
      renderHome();
    }
  };
}

function submitAnswer(q, correctShuffled) {
  if (state.selectedIdx === null) return;
  state.answered = true;
  const opts = document.querySelectorAll(".option");
  const correct = state.selectedIdx === correctShuffled;
  if (correct) state.correct++; else state.wrong++;
  if (!state.perDomain[q.domain]) state.perDomain[q.domain] = { right: 0, wrong: 0, total: 0 };
  state.perDomain[q.domain].total++;
  if (correct) state.perDomain[q.domain].right++;
  else state.perDomain[q.domain].wrong++;

  opts.forEach((opt, i) => {
    opt.classList.add("disabled");
    opt.classList.remove("selected");
    const isCorrect = parseInt(opt.dataset.correct) === 1;
    const isSelected = i === state.selectedIdx;
    if (isCorrect) opt.classList.add("correct");
    else if (isSelected) opt.classList.add("wrong");
    opt.onclick = null;
  });

  $("submitBtn").style.display = "none";
  $("nextBtn").style.display = "";
  $("nextBtn").textContent = (state.idx + 1 >= state.questions.length) ? "Finish →" : "Next question →";

  if (state.explain && !state.examMode) {
    const letters = ["A","B","C","D"];
    $("verdictContainer").innerHTML = `
      <div class="verdict ${correct ? "correct" : "wrong"}">
        <div class="verdict-title">${correct ? "Correct — " + letters[correctShuffled] : "Incorrect — correct answer was " + letters[correctShuffled]}</div>
        <div class="verdict-explanation">${q.explanation}</div>
      </div>
    `;
  }

  $("quizScore").innerHTML = `<span class="right">${state.correct}</span> correct · <span class="wrong">${state.wrong}</span> wrong`;
}

/* ---------- Summary ---------- */
function finishQuiz() {
  stopTimer();
  const total = state.correct + state.wrong;
  const pct = total === 0 ? 0 : Math.round((state.correct / total) * 100);
  // approximate scaled score 100-1000, with 720 being 70%
  const scaled = total === 0 ? 100 : Math.max(100, Math.min(1000, Math.round(100 + (state.correct / state.questions.length) * 900)));
  const pass = scaled >= 720;

  const breakdownRows = Object.keys(DOMAINS).map(d => {
    const s = state.perDomain[d] || { right: 0, wrong: 0, total: 0 };
    const p = s.total === 0 ? 0 : Math.round((s.right / s.total) * 100);
    return `<div class="breakdown-row">
      <span class="breakdown-name">${DOMAINS[d].short}</span>
      <div class="breakdown-bar"><div class="breakdown-bar-fill" style="width:${p}%"></div></div>
      <span class="breakdown-num">${s.right}/${s.total} · ${p}%</span>
    </div>`;
  }).join("");

  $("homeView").style.display = "none";
  $("quizView").style.display = "none";
  $("summaryView").style.display = "";
  $("summaryView").innerHTML = `
    <div class="summary-card">
      <h2>${state.examMode ? "Exam complete" : "Session complete"}</h2>
      <div class="big-score">${pct}%</div>
      <div class="scaled-score">${state.correct} of ${total} correct ${state.examMode ? ` · scaled ≈ ${scaled}/1000` : ""}</div>
      ${state.examMode ? `<div class="pass-pill ${pass ? "pass" : "fail"}">${pass ? "Pass (≥720)" : "Below 720 — keep practicing"}</div>` : ""}
    </div>
    <div class="summary-breakdown">
      <h4>By domain</h4>
      ${breakdownRows}
    </div>
    <div class="actions">
      <div class="actions-left">
        <button class="start-btn secondary" id="backHome">← Back to home</button>
      </div>
      <div class="actions-right">
        <button class="start-btn" id="againBtn">Practice again →</button>
      </div>
    </div>
  `;
  $("backHome").onclick = renderHome;
  $("againBtn").onclick = startQuiz;
}

/* ---------- Init ---------- */
window.addEventListener("DOMContentLoaded", () => {
  // Wait for bank to be present
  if (!window.QUESTION_BANK || window.QUESTION_BANK.length === 0) {
    document.querySelector(".container").innerHTML = "<p style='padding:40px;text-align:center;color:var(--text-muted)'>Question bank failed to load.</p>";
    return;
  }
  renderHome();
});

