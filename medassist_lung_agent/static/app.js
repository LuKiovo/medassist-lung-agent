const question = document.querySelector("#question");
const askBtn = document.querySelector("#askBtn");
const clearChatBtn = document.querySelector("#clearChatBtn");
const chatResult = document.querySelector("#chatResult");
const xrayFile = document.querySelector("#xrayFile");
const analyzeBtn = document.querySelector("#analyzeBtn");
const xrayResult = document.querySelector("#xrayResult");
const preview = document.querySelector("#preview");
const heatmap = document.querySelector("#heatmap");
const followUpCard = document.querySelector("#followUpCard");
const followUpCount = document.querySelector("#followUpCount");
const followUpButtons = document.querySelector("#followUpButtons");
const followUpInputs = document.querySelector("#followUpInputs");
const submitFollowUpBtn = document.querySelector("#submitFollowUpBtn");
const skipFollowUpBtn = document.querySelector("#skipFollowUpBtn");
const emergencyModal = document.querySelector("#emergencyModal");
const humanDoctorLink = document.querySelector("#humanDoctorLink");
const closeEmergencyBtn = document.querySelector("#closeEmergencyBtn");

let lastQuestion = "";
let lastFollowUpQuestions = [];

function setResult(node, text, empty = false) {
  node.textContent = text;
  node.classList.toggle("empty", empty);
}

function formatCitations(citations) {
  if (!citations || citations.length === 0) return "";
  return citations
    .map((item, index) => {
      const parts = item.source.replaceAll("\\", "/").split("/");
      return `[${index + 1}] ${parts[parts.length - 1]}`;
    })
    .join("\n");
}

function collectFollowUpAnswers() {
  const answers = {};
  followUpInputs.querySelectorAll("textarea[data-question]").forEach((input) => {
    const value = input.value.trim();
    if (value) {
      answers[input.dataset.question] = value;
    }
  });
  return answers;
}

function showEmergencyModal(data) {
  if (data.urgency !== "emergency") return;
  const url = data.emergency_resources?.human_doctor_url || "/docs";
  humanDoctorLink.href = url;
  emergencyModal.hidden = false;
}

function hideEmergencyModal() {
  emergencyModal.hidden = true;
}

function renderFollowUpCard(questions) {
  lastFollowUpQuestions = questions || [];
  followUpButtons.innerHTML = "";
  followUpInputs.innerHTML = "";
  followUpCount.textContent = `${lastFollowUpQuestions.length} 项`;
  if (lastFollowUpQuestions.length === 0) {
    followUpCard.hidden = true;
    return;
  }

  lastFollowUpQuestions.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "follow-up-chip";
    button.textContent = item;
    button.dataset.target = `follow-up-${index}`;
    followUpButtons.appendChild(button);

    const group = document.createElement("label");
    group.className = "follow-up-input";
    group.id = `follow-up-${index}`;
    group.hidden = true;
    group.textContent = item;

    const input = document.createElement("textarea");
    input.dataset.question = item;
    input.rows = 2;
    input.placeholder = "可选填写，例如：38.5℃，持续 1 天，没有基础病";
    group.appendChild(input);
    followUpInputs.appendChild(group);

    button.addEventListener("click", () => {
      group.hidden = false;
      input.focus();
    });
  });

  followUpCard.hidden = false;
}

function renderChatResult(data) {
  const meta = [
    data.intent ? `意图：${data.intent}` : "",
    data.urgency ? `紧急程度：${data.urgency}` : "",
  ]
    .filter(Boolean)
    .join(" | ");
  const redFlags = data.red_flags?.length ? `\n\n红旗提醒：${data.red_flags.join("、")}` : "";
  const actions = data.next_actions?.length ? `\n\n建议动作：\n${data.next_actions.map((x) => `- ${x}`).join("\n")}` : "";
  const sources = formatCitations(data.citations);
  setResult(
    chatResult,
    `${meta ? `${meta}\n\n` : ""}${data.answer}${redFlags}${actions}${sources ? `\n\n参考来源：\n${sources}` : ""}`
  );
}

async function askHealthQuestion(followUpAnswers = null) {
  const q = lastQuestion || question.value.trim();
  if (!q) {
    setResult(chatResult, "请先输入健康问题。", true);
    return null;
  }
  lastQuestion = q;
  setResult(chatResult, "正在检索知识库并生成回答...");
  const payload = { question: q, top_k: 4 };
  if (followUpAnswers) {
    payload.follow_up_answers = followUpAnswers;
  }
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    setResult(chatResult, `请求失败：${resp.status}`);
    return null;
  }
  const data = await resp.json();
  renderChatResult(data);
  renderFollowUpCard(data.follow_up_questions);
  showEmergencyModal(data);
  return data;
}

askBtn.addEventListener("click", async () => {
  lastQuestion = question.value.trim();
  await askHealthQuestion();
});

clearChatBtn.addEventListener("click", () => {
  question.value = "";
  lastQuestion = "";
  lastFollowUpQuestions = [];
  followUpCard.hidden = true;
  followUpButtons.innerHTML = "";
  followUpInputs.innerHTML = "";
  setResult(chatResult, "回答会显示在这里。", true);
});

submitFollowUpBtn.addEventListener("click", async () => {
  const answers = collectFollowUpAnswers();
  await askHealthQuestion(answers);
});

skipFollowUpBtn.addEventListener("click", async () => {
  const emptyAnswers = {};
  followUpInputs.querySelectorAll("textarea[data-question]").forEach((input) => {
    input.value = "";
  });
  await askHealthQuestion(emptyAnswers);
});

closeEmergencyBtn.addEventListener("click", hideEmergencyModal);

emergencyModal.addEventListener("click", (event) => {
  if (event.target === emergencyModal) {
    hideEmergencyModal();
  }
});

xrayFile.addEventListener("change", () => {
  const file = xrayFile.files?.[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  preview.style.display = "block";
  heatmap.style.display = "none";
  setResult(xrayResult, `已选择：${file.name}`, true);
});

analyzeBtn.addEventListener("click", async () => {
  const file = xrayFile.files?.[0];
  if (!file) {
    setResult(xrayResult, "请先选择胸部 X 光图片。", true);
    return;
  }
  const form = new FormData();
  form.append("file", file);
  setResult(xrayResult, "正在分析胸片...");
  const resp = await fetch("/api/xray/analyze", { method: "POST", body: form });
  if (!resp.ok) {
    setResult(xrayResult, `请求失败：${resp.status}`);
    return;
  }
  const data = await resp.json();
  const scores = Object.entries(data.scores)
    .map(([name, value]) => `${name}: ${(value * 100).toFixed(2)}%`)
    .join("\n");
  if (data.gradcam_png_base64) {
    heatmap.src = `data:image/png;base64,${data.gradcam_png_base64}`;
    heatmap.style.display = "block";
  }
  setResult(
    xrayResult,
    `预测：${data.prediction}\n\n概率：\n${scores}\n\n${data.risk_note}\n\n${data.medical_disclaimer}`
  );
});
