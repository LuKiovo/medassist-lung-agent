const question = document.querySelector("#question");
const askBtn = document.querySelector("#askBtn");
const clearChatBtn = document.querySelector("#clearChatBtn");
const chatResult = document.querySelector("#chatResult");
const xrayFile = document.querySelector("#xrayFile");
const analyzeBtn = document.querySelector("#analyzeBtn");
const xrayResult = document.querySelector("#xrayResult");
const preview = document.querySelector("#preview");
const heatmap = document.querySelector("#heatmap");

function setResult(node, text, empty = false) {
  node.textContent = text;
  node.classList.toggle("empty", empty);
}

function formatCitations(citations) {
  if (!citations || citations.length === 0) return "";
  return citations
    .map((item, index) => `\n[${index + 1}] ${item.source}\n${item.text.slice(0, 180)}...`)
    .join("\n");
}

askBtn.addEventListener("click", async () => {
  const q = question.value.trim();
  if (!q) {
    setResult(chatResult, "请先输入健康问题。", true);
    return;
  }
  setResult(chatResult, "正在检索知识库并生成回答...");
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: q, top_k: 4 }),
  });
  if (!resp.ok) {
    setResult(chatResult, `请求失败：${resp.status}`);
    return;
  }
  const data = await resp.json();
  const redFlags = data.red_flags?.length ? `\n\n红旗提醒：${data.red_flags.join("、")}` : "";
  setResult(chatResult, `${data.answer}${redFlags}\n\n参考片段：${formatCitations(data.citations)}`);
});

clearChatBtn.addEventListener("click", () => {
  question.value = "";
  setResult(chatResult, "回答会显示在这里。", true);
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
