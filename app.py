"""SmartTaxi RL - تطبيق ويب بالعربية. Run: streamlit run app.py"""
import time
from pathlib import Path

import arabic_reshaper
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from bidi.algorithm import get_display

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv
from experiments.evaluate import run_episode
from experiments.train import train

MODEL = Path(__file__).parent / "results" / "q_table.npz"
BLUE, ORANGE, GREEN = "#1F6F8B", "#E8743B", "#2EA05A"
ACTIONS_AR = ["أعلى ⬆", "أسفل ⬇", "يمين ➡", "يسار ⬅", "التقاط الراكب", "إنزال الراكب"]
plt.rcParams["font.family"] = "DejaVu Sans"


def ar(text):
    """Shape + reorder Arabic text so matplotlib draws it correctly."""
    return get_display(arabic_reshaper.reshape(text))


st.set_page_config(page_title="SmartTaxi RL — سيارة أجرة تتعلم", page_icon="🚕", layout="wide")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown,
[data-testid="stMetric"], [data-testid="stAlert"], label, h1, h2, h3, p { direction: rtl; text-align: right; }
[data-baseweb="slider"], [data-testid="stLatex"], .katex-display, code, [data-testid="stDataFrame"] { direction: ltr; }
button[role="tab"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

env = SmartTaxiEnv()
city = env.city

# ---------- الحالة ----------
if "agent" not in st.session_state:
    ag = QLearningAgent(env.num_states, env.NUM_ACTIONS)
    if MODEL.exists():
        ag.load(MODEL)
        st.session_state.source = "نموذج مدرَّب مسبقًا (30,000 حلقة)"
        st.session_state.pretrained = True
    else:
        st.session_state.source = "وكيل غير مدرَّب (كل القيم أصفار)"
        st.session_state.pretrained = False
    st.session_state.agent, st.session_state.rows = ag, None


def smooth(x, w=100):
    x = np.asarray(x, float)
    w = min(w, max(1, len(x)))
    return np.convolve(x, np.ones(w) / w, mode="valid")


def draw_map(path=None, k=0, pickup=None, dest=None, onboard_at=None):
    """Draw city + route. Route is orange before pickup and blue after; every cell visited is numbered."""
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    for (x, y) in city.OBSTACLES:
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color="#3C424E"))
    for i, (x, y) in enumerate(city.PICKUP_POINTS):
        ax.add_patch(plt.Circle((x + .5, y + .5), .33, color=GREEN if i == pickup else "#A9D4BB"))
        ax.text(x + .5, y + .5, f"P{i}", ha="center", va="center", color="white", fontsize=9, weight="bold")
    for i, (x, y) in enumerate(city.DESTINATIONS):
        ax.add_patch(plt.Rectangle((x + .15, y + .15), .7, .7, color=BLUE if i == dest else "#A9C6D2"))
        ax.text(x + .5, y + .5, f"D{i}", ha="center", va="center", color="white", fontsize=9, weight="bold")
    if path:
        pts = np.array(path[:k + 1]) + .5
        for i in range(1, len(pts)):
            col = BLUE if (onboard_at is not None and i > onboard_at) else ORANGE
            ax.annotate("", xy=pts[i], xytext=pts[i - 1],
                        arrowprops=dict(arrowstyle="->", color=col, lw=2, shrinkA=0, shrinkB=0))
        for i in range(len(pts)):
            ax.text(pts[i, 0] + .28, pts[i, 1] - .28, str(i), fontsize=7, color="#555", ha="center")
        ax.add_patch(plt.Rectangle((pts[-1, 0] - .3, pts[-1, 1] - .22), .6, .44, color="#F2B705",
                                   ec="black", lw=1.5, zorder=5))
    ax.set_xlim(0, city.WIDTH); ax.set_ylim(city.HEIGHT, 0); ax.set_aspect("equal")
    ax.set_xticks(range(city.WIDTH + 1)); ax.set_yticks(range(city.HEIGHT + 1))
    ax.grid(color="#D5D9E0"); ax.tick_params(labelsize=7, length=0)
    ax.set_facecolor("#E9ECF1")
    ax.set_xlabel(ar("x  (يمين ←)"), fontsize=8); ax.set_ylabel(ar("y  (للأسفل ↓)"), fontsize=8)
    fig.tight_layout()
    return fig


# ---------- الشريط الجانبي ----------
st.sidebar.title("🚕 SmartTaxi RL")
st.sidebar.caption("خوارزمية Q-Learning الجدولية على مدينة 10×10")
alpha = st.sidebar.select_slider("معدل التعلّم α", [0.01, 0.05, 0.1, 0.2, 0.5], 0.1)
gamma = st.sidebar.select_slider("معامل الخصم γ", [0.5, 0.8, 0.9, 0.95, 0.99], 0.95)
eps_decay = st.sidebar.select_slider("تناقص ε في كل حلقة", [0.99, 0.995, 0.999, 0.9995], 0.999)
episodes = st.sidebar.slider("عدد حلقات التدريب", 1000, 30000, 10000, 1000)
seed = st.sidebar.number_input("البذرة العشوائية", 0, 9999, 42)
if st.sidebar.button("▶ درّب وكيلًا جديدًا", type="primary"):
    bar = st.sidebar.progress(0.0, text="جارٍ التدريب...")
    ag, rows = train(episodes, seed=int(seed), alpha=alpha, gamma=gamma, epsilon_decay=eps_decay,
                     tag="_app", save=False,
                     on_progress=lambda e, n: bar.progress(e / n, text=f"الحلقة {e} من {n}"))
    bar.empty()
    st.session_state.agent, st.session_state.rows = ag, rows
    st.session_state.pretrained = False
    st.session_state.source = f"مدرَّب الآن: α={alpha}، γ={gamma}، {episodes} حلقة"
st.sidebar.info(f"الوكيل الحالي: {st.session_state.source}")
agent = st.session_state.agent

st.title("SmartTaxi RL — سيارة أجرة تتعلّم القيادة بخوارزمية Q-Learning")
t_learn, t_demo, t_eval, t_math = st.tabs(
    ["📈 التعلّم", "🚕 شاهد السيارة تتحرك", "⚖️ مقارنة مع العشوائي", "🧮 حاسبة تحديث Q"])

# ---------- التعلّم ----------
with t_learn:
    rows = st.session_state.rows
    csv = Path(__file__).parent / "results" / "training_results.csv"
    if rows is not None:
        df = pd.DataFrame(rows)
    elif st.session_state.pretrained and csv.exists():
        df = pd.read_csv(csv)
        st.caption("هذا سجل تدريب النموذج الجاهز. اضغط «درّب وكيلًا جديدًا» في الشريط الجانبي لتجربة إعداداتك.")
    else:
        df = None
    if df is None:
        st.info("اضغط «درّب وكيلًا جديدًا» في الشريط الجانبي.")
    else:
        c1, c2, c3 = st.columns(3)
        last = df.tail(200)
        c1.metric("نسبة النجاح (آخر 200 حلقة)", f"{last.success.mean():.0%}")
        c2.metric("متوسط المكافأة (آخر 200 حلقة)", f"{last.reward.mean():.1f}")
        c3.metric("قيمة ε النهائية", f"{df.epsilon.iloc[-1]:.3f}")
        f1, ax1 = plt.subplots(figsize=(6, 3.4))
        ax1.plot(smooth(df.reward), color=BLUE)
        ax1.set_title(ar("متوسط المكافأة لكل حلقة"), fontsize=11)
        ax1.set_xlabel(ar("رقم حلقة التدريب")); ax1.spines[["top", "right"]].set_visible(False); ax1.grid(alpha=.25)
        f2, ax2 = plt.subplots(figsize=(6, 3.4))
        ax2.plot(smooth(df.success) * 100, color=BLUE)
        ax3 = ax2.twinx(); ax3.plot(df.epsilon, color=ORANGE); ax3.set_ylabel("ε", color=ORANGE)
        ax2.set_title(ar("نسبة النجاح % (أزرق) و ε (برتقالي)"), fontsize=11)
        ax2.set_xlabel(ar("رقم حلقة التدريب")); ax2.spines[["top"]].set_visible(False); ax2.grid(alpha=.25)
        a, b = st.columns(2); a.pyplot(f1); b.pyplot(f2)
        f3, ax4 = plt.subplots(figsize=(12, 3))
        ax4.plot(df.episode, df.q_tracked, color=BLUE)
        ax4.set_title(ar("تغيّر قيمة Q واحدة: السيارة عند الراكب P0 والوجهة D0، الفعل = التقاط"), fontsize=11)
        ax4.set_xlabel(ar("رقم حلقة التدريب")); ax4.spines[["top", "right"]].set_visible(False); ax4.grid(alpha=.25)
        st.pyplot(f3)
        st.caption("تبدأ القيمة من 0 ثم ترتفع حتى تستقر قرب 87.1 (العائد المخصوم الحقيقي لهذه الحالة) بعد أن يكتشف الوكيل مكافأة التوصيل +100.")

# ---------- المشاهدة ----------
with t_demo:
    st.markdown("""
**كيف تتحرك السيارة؟** في كل خطوة تنظر إلى **صف الحالة الحالية** في جدول Q، وتختار **الفعل صاحب أكبر قيمة**.
الأفعال الأربعة الأولى تحرّكها خلية واحدة، وإن كانت الخلية المقصودة عائقًا أو خارج الخريطة تبقى مكانها وتأخذ عقوبة −20.
المسار البرتقالي: قبل التقاط الراكب، والأزرق: بعد التقاطه، والأرقام الصغيرة ترتّب الخلايا التي مرّت بها.
""")
    left, right = st.columns([1, 1])
    with left:
        c1, c2, c3, c4 = st.columns(4)
        pk = c1.selectbox("نقطة الراكب", range(4), format_func=lambda i: f"P{i} {city.PICKUP_POINTS[i]}")
        ds = c2.selectbox("الوجهة", range(4), format_func=lambda i: f"D{i} {city.DESTINATIONS[i]}")
        sx = c3.number_input("بداية x", 0, 9, 4)
        sy = c4.number_input("بداية y", 0, 9, 5)
        start = (int(sx), int(sy))
        if not city.is_free(*start):
            st.error("خلية البداية عائق، اختر خلية أخرى.")
            st.stop()
        e2 = SmartTaxiEnv()
        s = e2.reset(pickup=pk, dest=ds, start=start)
        path, states, acts, rewards, before_after, pick_at = [e2.taxi], [s], [], [], [], None
        while not e2.done:
            a = agent.choose_action(s, explore=False)
            prev, was_on = e2.taxi, e2.onboard
            s, r, *_ = e2.step(a)
            path.append(e2.taxi); states.append(s); acts.append(a); rewards.append(r)
            before_after.append((prev, e2.taxi))
            if e2.onboard and not was_on:
                pick_at = len(path) - 1
        k = st.slider("الخطوة", 0, len(path) - 1, len(path) - 1)
        play = st.button("▶ تشغيل متحرك")
        st.write(f"**النتيجة:** {'✅ تم التوصيل' if e2.success else '❌ لم يتم التوصيل'} خلال {e2.steps} خطوة · "
                 f"مجموع المكافآت {sum(rewards):.0f} · الاصطدامات {e2.collisions}")
        map_box = st.empty()
        map_box.pyplot(draw_map(path, k, pk, ds, pick_at))
    with right:
        info_box = st.empty()

        def show_info(k):
            with info_box.container():
                st.subheader(f"الخطوة {k}")
                x, y, p, d, b = env.decode(states[k])
                st.markdown(f"الحالة `(x={x}, y={y}, p={p}, d={d}, b={b})` ← صف رقم **{states[k]}** في الجدول")
                q = agent.q_table[states[k]]
                qdf = pd.DataFrame({"الفعل": ACTIONS_AR, "Q(s,a)": q.round(2)})
                qdf["المختار"] = ["◀" if (k < len(acts) and i == acts[k]) else "" for i in range(6)]
                st.dataframe(qdf, hide_index=True, width="stretch")
                if k < len(acts):
                    (px, py), (nx, ny) = before_after[k]
                    st.markdown(f"**القرار:** أكبر قيمة Q هي «{ACTIONS_AR[acts[k]]}» ← "
                                f"الموقع من ({px},{py}) إلى ({nx},{ny}) ← مكافأة **{rewards[k]}**")
                else:
                    st.markdown("**انتهت الرحلة.**")

        show_info(k)
        if play:
            for kk in range(len(path)):
                map_box.pyplot(draw_map(path, kk, pk, ds, pick_at))
                show_info(kk)
                time.sleep(0.5)
    st.markdown("#### جدول خطوات الرحلة")
    trip = pd.DataFrame({
        "الخطوة": range(1, len(acts) + 1),
        "من": [f"({a[0]},{a[1]})" for a, _ in before_after],
        "الفعل": [ACTIONS_AR[a] for a in acts],
        "إلى": [f"({b[0]},{b[1]})" for _, b in before_after],
        "المكافأة": rewards,
        "أكبر Q في الصف": [round(float(agent.q_table[states[i]].max()), 2) for i in range(len(acts))],
    })
    st.dataframe(trip, hide_index=True, width="stretch")

# ---------- المقارنة ----------
with t_eval:
    n = st.slider("عدد المهام الاختبارية", 50, 500, 200, 50)
    if st.button("شغّل المقارنة"):
        ev = SmartTaxiEnv()
        rnd = np.random.default_rng(0)
        res = {"عشوائي": [], "Q-Learning": []}
        for i in range(n):
            for name, pol in (("عشوائي", lambda s: int(rnd.integers(6))),
                              ("Q-Learning", lambda s: agent.choose_action(s, explore=False))):
                tot, info = run_episode(ev, 10_000 + i, pol)
                res[name].append((info["success"], info["steps"], tot, info["collisions"]))
        table = pd.DataFrame({k: {"نسبة النجاح": np.mean([r[0] for r in v]),
                                  "متوسط الخطوات": np.mean([r[1] for r in v]),
                                  "متوسط المكافأة": np.mean([r[2] for r in v]),
                                  "متوسط الاصطدامات": np.mean([r[3] for r in v])} for k, v in res.items()}).T
        st.dataframe(table.style.format({"نسبة النجاح": "{:.1%}", "متوسط الخطوات": "{:.1f}",
                                         "متوسط المكافأة": "{:.1f}", "متوسط الاصطدامات": "{:.2f}"}), width="stretch")
        st.bar_chart(table[["متوسط الخطوات"]])
        st.caption("الوكيلان يتلقيان المهام نفسها (بذرة واحدة لكل مهمة)، ويُقيَّم Q-Learning دون استكشاف عشوائي.")

# ---------- الحاسبة ----------
with t_math:
    st.latex(r"Q(s,a) \leftarrow Q(s,a) + \alpha\,[\,r + \gamma \max_{a'} Q(s',a') - Q(s,a)\,]")
    st.markdown("غيّر الأرقام لترى كيف تُحسب القيمة الجديدة. القيم الافتراضية هي مثال الشرائح: التقاط الراكب (r = 15 − 1 = 14).")
    c1, c2, c3 = st.columns(3)
    q_old = c1.number_input("Q(s,a) الحالية", value=0.0)
    r = c2.number_input("المكافأة r", value=14.0)
    q_next = c3.number_input("أكبر Q في الحالة التالية", value=20.0)
    c4, c5, c6 = st.columns(3)
    al = c4.number_input("α", 0.0, 1.0, 0.1, 0.01)
    ga = c5.number_input("γ", 0.0, 1.0, 0.95, 0.01)
    term = c6.checkbox("حالة نهائية (تم التوصيل)")
    target = r + (0 if term else ga * q_next)
    td = target - q_old
    new = q_old + al * td
    st.markdown(f"**الهدف** = r + γ·maxQ(s′) = {r} + {0 if term else ga}×{q_next} = **{target:.3f}**  \n"
                f"**خطأ الفرق الزمني** = {target:.3f} − {q_old:.3f} = **{td:.3f}**  \n"
                f"**Q الجديدة** = {q_old:.3f} + {al}×{td:.3f} = **{new:.3f}**")
    k_visits = st.slider("كرّر التحديث نفسه n مرة (الهدف ثابت)", 1, 50, 10)
    qs = [q_old]
    for _ in range(k_visits):
        qs.append(qs[-1] + al * (target - qs[-1]))
    st.line_chart(pd.DataFrame({"Q": qs}))
