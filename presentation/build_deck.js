const pptxgen = require("pptxgenjs");
const path = require("path");
const SK = "/root/.claude/skills/synced/6980f3d7-ebe2-4cff-8f69-1d30e4198671_0ae9443a-e405-42da-8fd4-dc5233dcb94b/pptx";
const { applyTheme } = require(SK + "/scripts/apply_theme.js");
const RES = path.resolve(__dirname, "../results");
const TRACE = JSON.parse(require("fs").readFileSync(path.join(RES, "trace.json"), "utf8"));
const AR_ACT = ["أعلى", "أسفل", "يمين", "يسار", "التقاط", "إنزال"];

const THEME = {
  name: "SmartTaxi", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "1B2430", lt1: "FFFFFF", dk2: "0F2A3A", lt2: "F1F3F6",
    accent1: "1F6F8B", accent2: "F2B705", accent3: "E8743B", accent4: "2EA05A",
    accent5: "8A8F98", accent6: "C9D3DD", hlink: "1F6F8B", folHlink: "8A8F98" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.title = "SmartTaxi RL";
const C = pres.SchemeColor;
const W = 13.33;

pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [],
  slideNumber: { x: 0.5, y: 7.05, w: 0.6, h: 0.3, fontSize: 11, color: "8A8F98" },
});
pres.defineSlideMaster({ title: "DARK", background: { color: "0F2A3A" } });

const rtl = (o = {}) => Object.assign({ isTextBox: true, rtlMode: true, align: "right", valign: "top", margin: 0, fontSize: 16, color: "1B2430" }, o);
const ltr = (o = {}) => Object.assign({ isTextBox: true, rtlMode: false, align: "left", valign: "middle", margin: 0, fontSize: 16, color: "1B2430" }, o);

function title(s, text, dark = false) {
  s.addText(text, rtl({ x: 0.6, y: 0.4, w: W - 1.2, h: 0.9, fontSize: 32, bold: true, valign: "middle", color: dark ? "FFFFFF" : "0F2A3A", objectName: "Title" }));
}
function card(s, x, y, w, h, fill = "F1F3F6", name = "Card") {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.12, objectName: name });
}
function badge(s, n, x, y, d = 0.5, fill = "F2B705", color = "0F2A3A") {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: "Badge" });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", bold: true, fontSize: 16, color, margin: 0, isTextBox: true, objectName: "BadgeText" });
}
function bullets(s, items, x, y, w, h, size = 18) {
  items = items.map(t => t.replace(/\.$/, ""));
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 10 } })),
    rtl({ x, y, w, h, fontSize: size }));
}
const img = (s, f, x, y, w, h) => s.addImage({ path: path.join(RES, f), x, y, w, h });

// 1 ── Title
let s = pres.addSlide({ masterName: "DARK" });
s.addText("SmartTaxi RL", ltr({ x: 0.8, y: 1.6, w: 11.7, h: 1.2, fontSize: 60, bold: true, color: "F2B705", align: "right", objectName: "Title" }));
s.addText("سيارة أجرة تتعلّم القيادة بنفسها باستخدام خوارزمية Q-Learning", rtl({ x: 0.8, y: 3.0, w: 11.7, h: 1.0, fontSize: 30, color: "FFFFFF", bold: true }));
s.addText("شرح مبسّط ودقيق: فضاء الحالات، المكافآت، معادلة التحديث، والتدريب", rtl({ x: 0.8, y: 4.1, w: 11.7, h: 0.6, fontSize: 20, color: "C9D3DD" }));
s.addText("حلقة بحثية  |  Python · NumPy · Pygame", rtl({ x: 0.8, y: 6.3, w: 11.7, h: 0.4, fontSize: 16, color: "8FA3B3" }));
s.addNotes("افتتاحية: المشروع يوضّح كيف يتعلّم وكيل (سيارة أجرة) سياسة قيادة من التجربة والخطأ فقط، دون أن نبرمج له المسار.");

// 2 ── RL idea
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "فكرة التعلّم المعزّز: وكيل، بيئة، مكافأة");
card(s, 5.4, 2.0, 2.5, 1.6, "0F2A3A", "AgentBox"); s.addText("Agent\nالسيارة الذكية", { x: 5.4, y: 2.0, w: 2.5, h: 1.6, align: "center", valign: "middle", color: "FFFFFF", bold: true, fontSize: 20, isTextBox: true, margin: 0 });
card(s, 5.4, 4.9, 2.5, 1.6, "1F6F8B", "EnvBox"); s.addText("Environment\nمدينة 10×10", { x: 5.4, y: 4.9, w: 2.5, h: 1.6, align: "center", valign: "middle", color: "FFFFFF", bold: true, fontSize: 20, isTextBox: true, margin: 0 });
s.addShape(pres.ShapeType.line, { x: 6.2, y: 3.6, w: 0, h: 1.3, line: { color: "E8743B", width: 3, endArrowType: "triangle" }, objectName: "ActionArrow" });
s.addShape(pres.ShapeType.line, { x: 7.1, y: 4.9, w: 0, h: -1.3, flipV: true, line: { color: "2EA05A", width: 3, endArrowType: "triangle" }, objectName: "StateArrow" });
s.addText("الفعل a", rtl({ x: 4.0, y: 3.95, w: 2.0, h: 0.5, fontSize: 18, bold: true, color: "E8743B", valign: "middle" }));
s.addText("الحالة s′ والمكافأة r", rtl({ x: 7.3, y: 3.95, w: 3.0, h: 0.5, fontSize: 18, bold: true, color: "2EA05A", valign: "middle", align: "left", rtlMode: false }));
bullets(s, ["الوكيل لا يعرف القواعد مسبقًا: يجرّب فعلًا ويرى النتيجة.", "المكافأة رقم يقول «أحسنت» أو «أخطأت».", "الهدف: اختيار أفعال تعظّم مجموع المكافآت على المدى الطويل.", "Q-Learning يخزّن «قيمة» كل فعل في كل حالة داخل جدول."], 0.6, 2.0, 4.5, 4.6, 18);
s.addNotes("نشرح الحلقة: الوكيل يرى الحالة s، يختار الفعل a، البيئة تعيد الحالة التالية s′ ومكافأة r، ثم يتكرر ذلك آلاف المرات.");

// 3 ── Environment
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "البيئة: مدينة شبكية بعوائق ثابتة");
img(s, "game_screenshot.png", 6.6, 1.55, 6.15, 4.1);
bullets(s, ["شبكة 10×10 = 100 خلية، منها 15 عائقًا ثابتًا.", "4 نقاط التقاط (P0–P3) و4 وجهات (D0–D3).", "في كل حلقة: موقع السيارة والراكب والوجهة عشوائيون.", "المهمة: اذهب إلى الراكب، التقطه، أوصله، ثم أنزله.", "تحقّق BFS أن كل نقطتين مهمتين متصلتان بمسار."], 0.6, 1.7, 5.7, 4.2, 18);
s.addText("لقطة من واجهة Pygame: P الأخضر راكب، D الأزرق وجهة، المستطيل الأصفر السيارة.", rtl({ x: 6.6, y: 5.8, w: 6.15, h: 0.7, fontSize: 14, color: "6B7280" }));
s.addNotes("هذه لقطة حقيقية من الواجهة. لاحظ لوحة Q على اليمين: تعرض قيم Q الستة للحالة الحالية، والأعلى هو الفعل الذي سيختاره الوكيل.");

// 4 ── State space
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "فضاء الحالات (State Space)");
s.addText("s = ( x , y , p , d , b )", ltr({ x: 0.6, y: 1.5, w: 12.1, h: 0.9, fontSize: 40, bold: true, align: "center", color: "1F6F8B", fontFace: "Cambria" }));
const parts = [["x , y", "موقع السيارة", "10 × 10"], ["p", "رقم نقطة الالتقاط", "4"], ["d", "رقم الوجهة", "4"], ["b", "الراكب بالسيارة؟ (0/1)", "2"]];
parts.forEach((p, i) => {
  const x = 0.6 + i * 3.05;
  card(s, x, 2.7, 2.85, 1.9, "F1F3F6", "StateCard");
  s.addText(p[0], ltr({ x, y: 2.8, w: 2.85, h: 0.6, fontSize: 28, bold: true, align: "center", color: "1F6F8B", fontFace: "Cambria" }));
  s.addText(p[1], rtl({ x: x + 0.15, y: 3.45, w: 2.55, h: 0.5, fontSize: 16, align: "center" }));
  s.addText(p[2] + " قيمة", rtl({ x: x + 0.15, y: 4.0, w: 2.55, h: 0.45, fontSize: 18, bold: true, align: "center", color: "E8743B" }));
});
s.addText("10 × 10 × 4 × 4 × 2 = 3200 حالة", ltr({ x: 0.6, y: 4.85, w: 12.1, h: 0.7, fontSize: 30, bold: true, align: "center", color: "0F2A3A" }));
s.addText("نحوّل كل حالة إلى رقم واحد هو فهرس الصف في الجدول، مثال:", rtl({ x: 0.6, y: 5.7, w: 12.1, h: 0.45, fontSize: 18 }));
s.addText("(3, 5, P1, D2, 0)  →  ((35·4 + 1)·4 + 2)·2 + 0 = 1132", ltr({ x: 0.6, y: 6.2, w: 12.1, h: 0.5, fontSize: 22, bold: true, align: "center", color: "1F6F8B" }));
s.addNotes("الحالة تحتوي كل ما يحتاجه الوكيل ليقرّر: أين أنا، أين الراكب والوجهة، وهل التقطت الراكب؟ حجم صغير (3200) هو ما يسمح باستخدام جدول عادي دون شبكة عصبية.");

// 5 ── Actions + Q table
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "الأفعال وجدول Q");
const acts = ["أعلى", "أسفل", "يمين", "يسار", "التقاط", "إنزال"];
acts.forEach((a, i) => {
  const x = 0.6 + i * 2.05;
  card(s, x, 1.55, 1.9, 1.0, i < 4 ? "1F6F8B" : "E8743B", "ActionCard");
  s.addText([{ text: String(i), options: { bold: true, fontSize: 22, breakLine: true } }, { text: a, options: { fontSize: 16 } }], { x, y: 1.55, w: 1.9, h: 1.0, align: "center", valign: "middle", color: "FFFFFF", isTextBox: true, margin: 0 });
});
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "0F2A3A" }, align: "center", fontSize: 14 } });
const cell = (t, o = {}) => ({ text: t, options: Object.assign({ align: "center", fontSize: 14, fontFace: "Arial" }, o) });
s.addTable([
  [hdr("حالة \\ فعل"), hdr("أعلى"), hdr("أسفل"), hdr("يمين"), hdr("يسار"), hdr("التقاط"), hdr("إنزال")],
  [cell("s = 0"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0")],
  [cell("s = 1132"), cell("…"), cell("…"), cell("…"), cell("…"), cell("…"), cell("…")],
  [cell("s = 3199"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0"), cell("0.0")],
], { x: 0.6, y: 3.0, w: 7.2, colW: [1.5, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95], rowH: 0.5, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "QTable" });
bullets(s, ["الجدول 3200 × 6 = 19200 قيمة، كلها صفر في البداية.", "Q(s,a) = «كم أتوقع أن أجمع من مكافآت إذا فعلت a في s ثم تصرفت جيدًا بعدها؟»", "القرار: في كل حالة نختار الفعل صاحب أكبر Q."], 8.2, 2.9, 4.55, 3.4, 16);
s.addNotes("هذا الجدول هو «ذاكرة» الوكيل بالكامل. التعلّم = تعديل هذه الأرقام تدريجيًا.");

// 6 ── Reward
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "دالة المكافأة (Reward)");
const rw = [["+100", "توصيل الراكب للوجهة الصحيحة", "2EA05A"], ["+15", "التقاط الراكب من مكانه الصحيح", "2EA05A"], ["−1", "كل خطوة (يشجّع الطرق القصيرة)", "8A8F98"], ["−10", "التقاط/إنزال في مكان خاطئ", "E8743B"], ["−20", "الاصطدام بعائق أو حافة الخريطة", "E8743B"], ["−15", "انتهاء 150 خطوة دون توصيل", "E8743B"]];
rw.forEach((r, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 6.75 - col * 6.15, y = 1.6 + row * 1.7;
  card(s, x, y, 5.95, 1.5, "F1F3F6", "RewardCard");
  s.addText(r[0], ltr({ x: x + 0.15, y, w: 1.9, h: 1.5, fontSize: 40, bold: true, color: r[2], align: "center" }));
  s.addText(r[1], rtl({ x: x + 2.1, y, w: 3.65, h: 1.5, fontSize: 17, valign: "middle" }));
});
s.addText("ملاحظة: كل خطوة تحمل عقوبة الخطوة، فتُجمع مع مكافأة الحدث (التقاط صحيح: 15 − 1 = 14)", rtl({ x: 0.6, y: 6.5, w: 12.1, h: 0.45, fontSize: 14, color: "6B7280" }));
s.addNotes("المكافآت هي الطريقة الوحيدة التي «نخبر» بها الوكيل عن الهدف. القيم اختيار تصميمي ابتدائي وليست قيمًا مثبتة كأمثل.");


// 6b ── How the car moves
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "كيف تتحرك السيارة؟ (قواعد الخطوة الواحدة)");
s.addText("المحور x نحو اليمين والمحور y نحو الأسفل. مثال: السيارة عند الخلية (4, 5)", rtl({ x: 0.6, y: 1.4, w: 12.1, h: 0.45, fontSize: 17, bold: true }));
const mv = [["أعلى", "0", "(0, −1)", "(4, 4)"], ["أسفل", "1", "(0, +1)", "(4, 6)"], ["يمين", "2", "(+1, 0)", "(5, 5)"], ["يسار", "3", "(−1, 0)", "(3, 5)"], ["التقاط", "4", "لا حركة", "ينجح فقط عند الراكب"], ["إنزال", "5", "لا حركة", "ينجح فقط عند الوجهة"]];
s.addTable([[hdr("الفعل"), hdr("الرقم"), hdr("التغيّر (dx, dy)"), hdr("الموقع الجديد")]].concat(mv.map(r => r.map((c, i) => cell(c, i == 0 ? { bold: true } : {})))),
  { x: 6.2, y: 2.0, w: 6.55, colW: [1.3, 0.9, 1.9, 2.45], rowH: 0.5, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "MoveTable" });
const rules = [["الخلية المقصودة حرّة", "تتحرك السيارة إليها", "r = −1", "2EA05A"], ["الخلية عائق أو خارج الخريطة", "تبقى مكانها وتأخذ عقوبة الاصطدام", "r = −1 − 20 = −21", "E8743B"]];
rules.forEach((r, i) => { const y = 2.0 + i * 1.55; card(s, 0.6, y, 5.3, 1.4, "F1F3F6", "RuleCard"); s.addText(r[0], rtl({ x: 0.8, y: y + 0.1, w: 4.9, h: 0.45, fontSize: 18, bold: true, color: r[3] })); s.addText(r[1], rtl({ x: 0.8, y: y + 0.58, w: 4.9, h: 0.35, fontSize: 16 })); s.addText(r[2], ltr({ x: 0.8, y: y + 0.95, w: 4.9, h: 0.35, fontSize: 17, bold: true, align: "right" })); });
card(s, 0.6, 5.2, 5.3, 1.4, "0F2A3A", "ExampleCard");
s.addText("مثال: السيارة عند الخلية (4, 0) وتختار «أعلى»", rtl({ x: 0.8, y: 5.28, w: 4.9, h: 0.4, fontSize: 16, bold: true, color: "FFFFFF" }));
s.addText("الخلية المقصودة خارج الخريطة، فتبقى مكانها", rtl({ x: 0.8, y: 5.68, w: 4.9, h: 0.4, fontSize: 15, color: "C9D3DD" }));
s.addText("(4, 0) → (4, 0),   r = −21", ltr({ x: 0.8, y: 6.1, w: 4.9, h: 0.4, fontSize: 18, bold: true, color: "F2B705", align: "right" }));
s.addText("اختيار الفعل نفسه يأتي من جدول Q: السيارة تنظر إلى صف حالتها وتختار الفعل صاحب أكبر قيمة", rtl({ x: 6.2, y: 5.5, w: 6.55, h: 1.0, fontSize: 17, bold: true, color: "1F6F8B" }));
s.addNotes("هذه قواعد البيئة (environment/taxi_env.py). لا يوجد تسارع أو اتجاه للسيارة: كل فعل يحرّك خلية واحدة فقط.");

// 7 ── Q formula
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "معادلة Q-Learning");
card(s, 0.6, 1.5, 12.1, 1.3, "0F2A3A", "FormulaBox");
s.addText("Q(s,a)  ←  Q(s,a) + α · [ r + γ · max Q(s′,a′) − Q(s,a) ]", ltr({ x: 0.6, y: 1.5, w: 12.1, h: 1.3, fontSize: 30, bold: true, align: "center", color: "FFFFFF", fontFace: "Arial" }));
const terms = [["Q(s,a)", "القيمة الحالية في الجدول"], ["α = 0.1", "معدل التعلّم: حجم الخطوة نحو الهدف"], ["r", "المكافأة الفورية بعد الفعل"], ["γ = 0.95", "الخصم: وزن المستقبل (القريب أهم)"], ["max Q(s′,·)", "أفضل قيمة متاحة في الحالة التالية"]];
terms.forEach((t, i) => {
  const x = 10.4 - i * 2.45;
  card(s, x, 3.1, 2.3, 1.9, "F1F3F6", "TermCard");
  s.addText(t[0], ltr({ x, y: 3.15, w: 2.3, h: 0.7, fontSize: 20, bold: true, align: "center", color: "1F6F8B", fontFace: "Cambria" }));
  s.addText(t[1], rtl({ x: x + 0.12, y: 3.85, w: 2.06, h: 1.1, fontSize: 14, align: "center" }));
});
s.addText([
  { text: "الهدف (Target) = r + γ · max Q(s′,a′)", options: { bold: true, breakLine: true } },
  { text: "خطأ الفرق الزمني (TD error) = Target − Q(s,a)", options: { bold: true, breakLine: true } },
  { text: "الفكرة: نحرّك Q خطوة صغيرة (α) باتجاه الهدف", options: { breakLine: true } },
  { text: "وإذا كانت الحالة نهائية (تم التوصيل) نحذف حد المستقبل ويصبح الهدف هو المكافأة فقط", options: {} },
], rtl({ x: 0.6, y: 5.3, w: 12.1, h: 1.5, fontSize: 17, paraSpaceAfter: 6 }));
s.addNotes("المعادلة تقول: القيمة الجديدة = القيمة القديمة + α × (ما حصلت عليه فعلًا − ما كنت أتوقعه). ما حصلت عليه فعلًا = المكافأة الآن + أفضل ما أتوقعه من الحالة التالية مخصومًا بـ γ.");

// 8 ── Worked example
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "مثال عددي: كيف تتغير Q مع كل عيّنة");
s.addText("الحالة: السيارة عند الراكب P0، الفعل: التقاط. r = 15 − 1 = 14. نفترض max Q(s′) = 20.", rtl({ x: 0.6, y: 1.4, w: 12.1, h: 0.5, fontSize: 17, bold: true }));
s.addText("Target = 14 + 0.95 × 20 = 33", ltr({ x: 0.6, y: 1.95, w: 12.1, h: 0.5, fontSize: 22, bold: true, color: "E8743B", align: "center", fontFace: "Cambria" }));
let q = 0; const rows = [[hdr("المرور"), hdr("Q قبل"), hdr("TD error = 33 − Q"), hdr("Q بعد = Q + 0.1·TD")]];
const series = [0];
for (let n = 1; n <= 10; n++) { const td = 33 - q, nq = q + 0.1 * td; if (n <= 3) rows.push([cell(String(n)), cell(q.toFixed(2)), cell(td.toFixed(2)), cell(nq.toFixed(2), { bold: true, color: "1F6F8B" })]); q = nq; series.push(+q.toFixed(2)); }
rows.push([cell("…"), cell("…"), cell("→ 0"), cell("→ 33", { bold: true, color: "2EA05A" })]);
s.addTable(rows, { x: 0.6, y: 2.7, w: 6.2, colW: [1.0, 1.4, 1.9, 1.9], rowH: 0.55, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "UpdateTable" });
s.addChart(pres.charts.LINE, [{ name: "Q(s,Pickup)", labels: series.map((_, i) => String(i)), values: series }], {
  x: 7.1, y: 2.6, w: 5.65, h: 3.6, showTitle: true, title: "Q(s, Pickup) after n visits", titleFontSize: 14, titleColor: "1B2430", chartColors: ["1F6F8B"],
  lineSize: 3, lineDataSymbolSize: 7, catAxisLabelColor: "6B7280", valAxisLabelColor: "6B7280", catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
  valGridLine: { color: "E3E7EC", size: 0.75 }, catGridLine: { style: "none" }, showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 35,
  showCatAxisTitle: true, catAxisTitle: "visits n", catAxisTitleFontSize: 12, catAxisTitleColor: "6B7280",
});
s.addText("كل مرور يقرّب Q من الهدف بنسبة 10% من الخطأ المتبقي، ولهذا يلزم عدد كبير من الحلقات", rtl({ x: 0.6, y: 6.2, w: 12.1, h: 0.4, fontSize: 16 }));
s.addText("Qn = 33 · (1 − 0.9^n)", ltr({ x: 0.6, y: 6.6, w: 12.1, h: 0.35, fontSize: 16, bold: true, color: "1F6F8B", align: "center" }));
s.addNotes("هذه الأرقام ناتجة فعلًا من الكود (experiments/explain_q.py). في التدريب الحقيقي يتغير max Q(s′) نفسه أيضًا، فتنتشر القيم من الحالة النهائية إلى الخلف.");

// 9 ── epsilon greedy
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "الاستكشاف مقابل الاستغلال (ε-greedy)");
img(s, "training_success.png", 6.4, 1.55, 6.35, 3.63);
bullets(s, ["استكشاف: فعل عشوائي باحتمال ε", "استغلال: أفضل فعل حسب Q باحتمال 1 − ε", "نبدأ بالاستكشاف الكامل (ε = 1)", "نقلّل ε بعد كل حلقة حتى حدّ أدنى", "نصل إلى الحد الأدنى تقريبًا عند الحلقة 3000"], 0.6, 1.6, 5.5, 3.3, 18);
card(s, 0.6, 5.05, 5.5, 1.2, "0F2A3A", "EpsCard");
s.addText("ε ← max( 0.05 , ε × 0.999 )", ltr({ x: 0.6, y: 5.05, w: 5.5, h: 1.2, fontSize: 24, bold: true, align: "center", color: "F2B705" }));
s.addText("الأزرق: نسبة النجاح (متوسط 100 حلقة)، البرتقالي: قيمة ε، وكلما قلّ الاستكشاف ارتفع النجاح", rtl({ x: 6.4, y: 5.3, w: 6.35, h: 0.8, fontSize: 14, color: "6B7280" }));
s.addNotes("بدون استكشاف قد يتمسّك الوكيل بأول مسار وجده. بدون استغلال لا يستفيد مما تعلّمه.");


// 9b ── epsilon calculation
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "كيف تُحسب ε وكيف تُستخدم في كل خطوة");
card(s, 0.6, 1.5, 5.6, 1.2, "0F2A3A", "EpsFormula");
s.addText("εₙ = max( 0.05 , 0.999ⁿ )", ltr({ x: 0.6, y: 1.5, w: 5.6, h: 1.2, fontSize: 28, bold: true, align: "center", color: "F2B705", fontFace: "Arial" }));
const epsKeys = Object.keys(TRACE.epsilon).filter(k => +k <= 3000);
s.addTable([[hdr("الحلقة n"), hdr("ε")]].concat(epsKeys.map(k => [cell(k), cell(String(TRACE.epsilon[k]), { bold: true, color: "E8743B" })])),
  { x: 0.6, y: 2.9, w: 5.6, colW: [2.8, 2.8], rowH: 0.38, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "EpsTable" });
const epsX = [], epsY = []; for (let n = 0; n <= 4000; n += 200) { epsX.push(String(n)); epsY.push(+Math.max(0.05, Math.pow(0.999, n)).toFixed(3)); }
s.addChart(pres.charts.LINE, [{ name: "epsilon", labels: epsX, values: epsY }], {
  x: 6.5, y: 1.4, w: 6.25, h: 3.8, showTitle: true, title: "epsilon vs training episode", titleFontSize: 14, titleColor: "1B2430", chartColors: ["E8743B"],
  lineSize: 3, lineDataSymbolSize: 4, catAxisLabelColor: "6B7280", valAxisLabelColor: "6B7280", catAxisLabelFontSize: 11, valAxisLabelFontSize: 12,
  valGridLine: { color: "E3E7EC", size: 0.75 }, catGridLine: { style: "none" }, showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 1 });
const dec = [["نسحب عددًا عشوائيًا u بين 0 و1", "مثال عند ε = 0.37 (الحلقة 1000)", "8A8F98"], ["u = 0.21 أصغر من ε", "نستكشف: نختار فعلًا عشوائيًا", "E8743B"], ["u = 0.74 أكبر من ε", "نستغل: نختار الفعل صاحب أكبر Q", "2EA05A"]];
dec.forEach((d, i) => { const x = 10.1 - i * 3.3; card(s, x, 5.4, 3.1, 1.4, "F1F3F6", "DecisionCard"); s.addText(d[0], rtl({ x: x + 0.15, y: 5.48, w: 2.8, h: 0.6, fontSize: 15, bold: true, color: d[2] })); s.addText(d[1], rtl({ x: x + 0.15, y: 6.1, w: 2.8, h: 0.65, fontSize: 14 })); });
s.addNotes("ε تتناقص مرة واحدة في نهاية كل حلقة (وليس كل خطوة). عند الحلقة 3000 تصل إلى الحد الأدنى 0.05، أي 5% استكشاف و95% استغلال.");

// 10 ── training loop
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "حلقة التدريب خطوة بخطوة");
const st = ["env.reset(): مهمة جديدة (موقع، راكب، وجهة عشوائية)", "اختيار الفعل a بسياسة ε-greedy", "env.step(a) ← الحالة التالية s′ والمكافأة r", "تحديث Q(s,a) بالمعادلة، ثم s ← s′", "نكرّر حتى التوصيل أو 150 خطوة، ثم نخفّض ε"];
st.forEach((t, i) => { const y = 1.55 + i * 1.02; badge(s, i + 1, 12.2, y + 0.1); card(s, 6.3, y, 5.75, 0.8, "F1F3F6", "StepCard"); s.addText(t, rtl({ x: 6.4, y, w: 5.55, h: 0.8, fontSize: 16, valign: "middle" })); });
card(s, 0.6, 1.55, 5.4, 4.9, "0F2A3A", "CodeCard");
s.addText([
  { text: "for ep in range(30000):", options: { breakLine: true } },
  { text: "  s = env.reset()", options: { breakLine: true } },
  { text: "  while True:", options: { breakLine: true } },
  { text: "    a = agent.choose_action(s)", options: { breakLine: true } },
  { text: "    s2, r, done, ... = env.step(a)", options: { breakLine: true } },
  { text: "    agent.update(s, a, r, s2, done)", options: { breakLine: true } },
  { text: "    s = s2", options: { breakLine: true } },
  { text: "    if done: break", options: { breakLine: true } },
  { text: "  agent.decay_epsilon()", options: {} },
], ltr({ x: 0.85, y: 1.7, w: 4.95, h: 4.6, fontSize: 15, fontFace: "Courier New", color: "F2B705", valign: "top" }));
s.addNotes("هذا هو الكود الفعلي في experiments/train.py. كل تحديث يمس خانة واحدة فقط من الجدول: Q[s, a].");


// 10b ── One episode, step by step
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "جولة واحدة خطوة بخطوة (من جدول Q المدرَّب)");
s.addText("المهمة: الراكب عند P0 (0,0)، الوجهة D0 (4,0)، والسيارة تبدأ عند (1,0). في كل خطوة تختار أكبر Q في الصف", rtl({ x: 0.6, y: 1.4, w: 12.1, h: 0.45, fontSize: 16, bold: true }));
const trRows = TRACE.steps.map(t => [cell(String(t.step)), cell(`(${t.before[0]},${t.before[1]})`), cell(AR_ACT[t.action], { bold: true }), cell(`(${t.after[0]},${t.after[1]})`), cell(String(t.reward), { color: t.reward > 0 ? "2EA05A" : "6B7280", bold: t.reward > 0 }), cell(t.q_chosen.toFixed(2), { color: "1F6F8B", bold: true })]);
s.addTable([[hdr("الخطوة"), hdr("الموقع قبل"), hdr("الفعل المختار"), hdr("الموقع بعد"), hdr("المكافأة r"), hdr("Q للفعل المختار")]].concat(trRows),
  { x: 0.6, y: 2.0, w: 7.6, colW: [0.9, 1.3, 1.5, 1.3, 1.2, 1.4], rowH: 0.5, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "EpisodeTable" });
bullets(s, ["الخطوة 2: يلتقط الراكب فيتحوّل b من 0 إلى 1", "الخطوة 7: الإنزال عند الوجهة ينهي الحلقة بالمكافأة الكبرى", "تزداد Q كلما اقتربنا من الوجهة لأن المكافأة النهائية تصبح أقرب"], 8.5, 2.0, 4.25, 2.2, 16);
s.addText("pickup: 15 − 1 = 14      dropoff: 100 − 1 = 99", ltr({ x: 8.5, y: 4.15, w: 4.25, h: 0.4, fontSize: 14, bold: true, color: "E8743B" }));
card(s, 8.5, 4.75, 4.25, 1.9, "0F2A3A", "CheckCard");
s.addText("تحقّق يدوي من الجدول", rtl({ x: 8.7, y: 4.82, w: 3.9, h: 0.4, fontSize: 16, bold: true, color: "F2B705" }));
s.addText([{ text: "Q7 = 99", options: { breakLine: true } }, { text: "Q6 = −1 + 0.95 × 99 = 93.05", options: { breakLine: true } }, { text: "Q5 = −1 + 0.95 × 93.05 = 87.40", options: {} }], ltr({ x: 8.7, y: 5.25, w: 3.9, h: 1.3, fontSize: 15, color: "FFFFFF", valign: "top" }));
s.addNotes("هذه الأرقام من الجدول المدرَّب فعلًا (experiments/trace_episode.py). التحقق اليدوي يثبت أن الجدول وصل إلى القيم النظرية: Q = r + γ × Q التالية.");

// 10c ── Backward propagation of values
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "كيف تنتشر القيمة إلى الخلف أثناء التدريب");
s.addText("نبدأ من جدول أصفار ونكرّر المسار نفسه (للتوضيح فقط). كل مرور يحدّث الخطوات بالترتيب بمعادلة Q", rtl({ x: 0.6, y: 1.4, w: 12.1, h: 0.45, fontSize: 16, bold: true }));
const snapKeys = Object.keys(TRACE.snapshots);
const bpRows = TRACE.steps.map((t, i) => [cell(`${t.step}: ${AR_ACT[t.action]}`, { bold: true })].concat(snapKeys.map(k => cell(TRACE.snapshots[k][i].toFixed(2), { color: i == 6 ? "2EA05A" : "1B2430" }))).concat([cell(t.q_chosen.toFixed(2), { color: "1F6F8B", bold: true })]));
s.addTable([[hdr("الخطوة والفعل")].concat(snapKeys.map(k => hdr("بعد " + k + (k == "1" ? " مرور" : " مرات")))).concat([hdr("المدرَّب")])].concat(bpRows),
  { x: 0.6, y: 1.95, w: 8.1, colW: [1.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.4], rowH: 0.48, border: { type: "solid", color: "C9D3DD", pt: 1 }, objectName: "PropagationTable" });
card(s, 8.95, 1.95, 3.8, 4.5, "F1F3F6", "WhyCard");
s.addText([
  { text: "لماذا تتحرك القيم بهذا الشكل؟", options: { bold: true, breakLine: true, color: "1F6F8B", fontSize: 17 } },
  { text: "المرور 1: لا تعرف الخطوات الأخرى شيئًا بعد، فقط الإنزال يتغيّر إلى 9.9", options: { breakLine: true } },
  { text: "المرور 2: الخطوة 6 ترى أن قيمة الحالة التالية صارت 9.9 فترتفع", options: { breakLine: true } },
  { text: "المرور 3 وما بعده: يصل الأثر إلى الخطوات السابقة تدريجيًا حتى الخطوة الأولى", options: {} },
], rtl({ x: 9.1, y: 2.05, w: 3.5, h: 4.3, fontSize: 15, paraSpaceAfter: 8 }));
s.addText("مثالان من الجدول: الإنزال في المرور 1، والخطوة 6 في المرور 2", rtl({ x: 0.6, y: 5.85, w: 8.1, h: 0.35, fontSize: 15, bold: true }));
s.addText("9.9 = 0.1 × (99 − 0)        0.75 = −0.1 + 0.1 × ( −1 + 0.95 × 9.9 + 0.1 )", ltr({ x: 0.6, y: 6.25, w: 8.1, h: 0.4, fontSize: 15, bold: true, color: "E8743B" }));
s.addNotes("هذه هي فكرة الانتشار إلى الخلف: المكافأة النهائية +100 لا تصل إلى بداية المسار إلا بعد تكرار التحديث عبر عدد كبير من الحلقات. لذلك يحتاج الوكيل آلاف الحلقات.");

// 11 ── Q growth
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "ماذا تعلّمت الأرقام فعلًا؟");
img(s, "q_value_growth.png", 0.6, 1.5, 8.0, 3.2);
card(s, 8.9, 1.5, 3.85, 3.2, "F1F3F6", "NoteCard");
s.addText("القيمة المتعلّمة استقرت عند 87.1", rtl({ x: 9.05, y: 1.6, w: 3.55, h: 1.0, fontSize: 18, bold: true, color: "1F6F8B" }));
s.addText("وهي القيمة النظرية المتوقعة للمسار الأقصر:", rtl({ x: 9.05, y: 2.55, w: 3.55, h: 0.7, fontSize: 15 }));
s.addText("14 − (0.95 + 0.95² + 0.95³ + 0.95⁴)\n+ 0.95⁵ · 99", ltr({ x: 9.05, y: 3.3, w: 3.55, h: 1.2, fontSize: 15, bold: true, valign: "top", color: "0F2A3A" }));
bullets(s, ["ارتفعت Q بسرعة بين الحلقات 1000 و3000 عندما بدأ الوكيل يصل إلى التوصيل ويكتشف المكافأة +100.", "المتوسط العام لأفضل Q يستمرّ بالارتفاع ببطء لأن حالات نادرة تُزار قليلًا وتحتاج مزيدًا من العيّنات."], 0.6, 4.95, 12.1, 1.9, 17);
s.addNotes("نقطة مهمة: القيمة 87.1 يمكن التحقق منها يدويًا، أي أن الجدول تقارب إلى القيمة الصحيحة وليس مجرد 'يبدو جيدًا'.");

// 12 ── Learning curves
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "منحنيات التعلّم");
img(s, "training_reward.png", 0.6, 1.5, 6.0, 3.43);
img(s, "training_success.png", 6.75, 1.5, 6.0, 3.43);
bullets(s, ["في البداية المكافأة سالبة جدًا (حتى −440): السيارة تصطدم وتنتهي مهلتها.", "بين 1000 و3000 حلقة: قفزة من 29% إلى 100% نجاح (في التدريب).", "بعدها تتحسّن المكافأة ببطء من ≈65 إلى ≈85 لأن الطرق تقصر."], 0.6, 5.1, 12.1, 1.8, 17);
s.addNotes("المكافأة تُحسب أثناء التدريب مع استكشاف ε، لذلك تقل قليلًا عن نتائج التقييم الحريصة.");

// 13 ── Eval vs random
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "التقييم: Q-Learning مقابل الوكيل العشوائي");
img(s, "agent_comparison.png", 0.6, 1.45, 12.1, 3.63);
const stats = [["100%", "نجاح Q-Learning"], ["0.8%", "نجاح العشوائي"], ["20.8", "متوسط الخطوات (مقابل 149.6)"], ["0", "اصطدامات (مقابل 23.2)"]];
stats.forEach((t, i) => { const x = 10.0 - i * 3.05; s.addText(t[0], ltr({ x, y: 5.2, w: 2.75, h: 0.8, fontSize: 38, bold: true, align: "center", color: i == 1 ? "8A8F98" : "1F6F8B" })); s.addText(t[1], rtl({ x, y: 6.0, w: 2.75, h: 0.6, fontSize: 14, align: "center" })); });
s.addNotes("500 مهمة بنفس البذور للوكيلين، دون استكشاف عند Q-Learning. ملاحظة صدق علمي: بعد 10000 حلقة فقط كانت النسبة 95.6%، وبعد 30000 حلقة 100%.");

// 14 ── Hyper-params
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "تأثير المعاملات (3 بذور × 6000 حلقة)");
img(s, "sweep.png", 0.6, 1.45, 12.1, 3.54);
bullets(s, ["معدل التعلّم صغير جدًا (0.01) بطيء: نجاح 53.5% فقط، أما 0.1 و0.5 فوصلا إلى 100%", "خصم قصير النظر (γ = 0.5) أضعف: نجاح 92.4% بانحراف 3.3، بينما 0.95 و0.99 وصلا إلى 100%", "قيم تناقص ε الثلاث نجحت هنا، والفرق في سرعة الوصول وليس في النتيجة النهائية"], 0.6, 5.15, 12.1, 1.8, 17);
s.addNotes("النتائج المعروضة بين قوسين في وسيلة الإيضاح هي نسبة النجاح النهائية لكل إعداد. الحالة محدودة بخريطة صغيرة، فلا نعمّم على بيئات أكبر.");

// 15 ── UI / how to run
s = pres.addSlide({ masterName: "CONTENT" }); title(s, "التشغيل والواجهة");
card(s, 0.6, 1.55, 6.3, 4.6, "0F2A3A", "RunCard");
s.addText([
  { text: "pip install -r requirements.txt", options: { breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "python -m experiments.train", options: { breakLine: true } },
  { text: "python -m experiments.evaluate", options: { breakLine: true } },
  { text: "python -m experiments.sweep", options: { breakLine: true } },
  { text: "python -m experiments.plot_results", options: { breakLine: true } },
  { text: "python -m experiments.explain_q", options: { breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "python main.py   # Pygame", options: {} },
], ltr({ x: 0.85, y: 1.75, w: 5.8, h: 4.2, fontSize: 16, fontFace: "Courier New", color: "F2B705", valign: "top" }));
bullets(s, ["ملف main.py يفتح نافذة Pygame تعرض السيارة وقيم Q للحالة الحالية", "مفتاح SPACE يشغّل الوكيل ويوقفه، وN خطوة واحدة، وR مهمة جديدة", "الأسهم مع P وD للقيادة اليدوية ومقارنتها بقرار الوكيل", "النتائج تُحفظ في مجلد results: ملفات CSV وصور وجدول Q"], 7.2, 1.7, 5.55, 4.4, 17);
s.addNotes("يمكن تشغيل النافذة أثناء العرض: اضغط N وراقب كيف يختار الفعل صاحب أكبر قيمة Q.");

// 16 ── Conclusion
s = pres.addSlide({ masterName: "DARK" }); title(s, "الخلاصة والقيود", true);
s.addText([
  { text: "حلّ Q-Learning الجدولي المسألة: 3200 حالة و6 أفعال ونجاح 100% في 500 مهمة تقييم", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "التعلّم هو تحديث متكرر لخانة واحدة في الجدول بخطوة صغيرة نحو الهدف", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "سياسة ε-greedy توازن بين الاستكشاف والاستغلال، ومعاملا α وγ يغيّران سرعة التعلّم وجودته", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "القيود: خريطة وعوائق ثابتة وأربع نقاط فقط وبلا فيزياء، فلا يُعدّ ذلك دليلًا على جاهزية قيادة حقيقية", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "عمل مستقبلي: عوائق متحركة وحالات أكبر وشبكة Deep Q-Network", options: { bullet: true } },
], rtl({ x: 0.8, y: 1.7, w: 11.7, h: 4.8, fontSize: 20, color: "FFFFFF" }));
s.addNotes("اختم بأن النتائج مخصّصة لبيئة المحاكاة المصمّمة، وأن الجدول لا يتسع لحالات أكبر دون تقريب الدوال.");

(async () => {
  const f = path.join(__dirname, "SmartTaxi_RL_Presentation.pptx");
  await pres.writeFile({ fileName: f });
  await applyTheme(f, THEME);
  console.log("written", f);
})();
