"""SmartTaxi RL - Streamlit app. Run: streamlit run app.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv
from experiments.evaluate import run_episode
from experiments.train import train

MODEL = Path(__file__).parent / "results" / "q_table.npz"
BLUE, ORANGE, GRAY = "#1F6F8B", "#E8743B", "#8A8F98"

st.set_page_config(page_title="SmartTaxi RL", page_icon="🚕", layout="wide")
env = SmartTaxiEnv()
city = env.city


# ---------- state ----------
if "agent" not in st.session_state:
    ag = QLearningAgent(env.num_states, env.NUM_ACTIONS)
    if MODEL.exists():
        ag.load(MODEL)
        st.session_state.source = "pre-trained model (30,000 episodes)"
    else:
        st.session_state.source = "untrained (all zeros)"
    st.session_state.agent, st.session_state.rows = ag, None


def smooth(x, w=100):
    x = np.asarray(x, float)
    w = min(w, max(1, len(x)))
    return np.convolve(x, np.ones(w) / w, mode="valid")


def draw_map(path=None, k=0, pickup=None, dest=None, onboard=False):
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    for (x, y) in city.OBSTACLES:
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color="#3C424E"))
    for i, (x, y) in enumerate(city.PICKUP_POINTS):
        on = i == pickup and not onboard
        ax.add_patch(plt.Circle((x + .5, y + .5), .33, color="#2EA05A" if on else "#A9D4BB"))
        ax.text(x + .5, y + .5, f"P{i}", ha="center", va="center", color="white", fontsize=9, weight="bold")
    for i, (x, y) in enumerate(city.DESTINATIONS):
        ax.add_patch(plt.Rectangle((x + .15, y + .15), .7, .7, color=BLUE if i == dest else "#A9C6D2"))
        ax.text(x + .5, y + .5, f"D{i}", ha="center", va="center", color="white", fontsize=9, weight="bold")
    if path:
        pts = np.array(path[:k + 1]) + .5
        ax.plot(pts[:, 0], pts[:, 1], color=ORANGE, lw=2, alpha=.8)
        ax.add_patch(plt.Rectangle((pts[-1, 0] - .3, pts[-1, 1] - .22), .6, .44, color="#F2B705", ec="black", lw=1.5, zorder=5))
    ax.set_xlim(0, city.WIDTH); ax.set_ylim(city.HEIGHT, 0); ax.set_aspect("equal")
    ax.set_xticks(range(city.WIDTH + 1)); ax.set_yticks(range(city.HEIGHT + 1))
    ax.grid(color="#D5D9E0"); ax.tick_params(labelsize=7, length=0)
    ax.set_facecolor("#E9ECF1")
    fig.tight_layout()
    return fig


# ---------- sidebar ----------
st.sidebar.title("🚕 SmartTaxi RL")
st.sidebar.caption("Tabular Q-Learning on a 10×10 city")
alpha = st.sidebar.select_slider("Learning rate α", [0.01, 0.05, 0.1, 0.2, 0.5], 0.1)
gamma = st.sidebar.select_slider("Discount γ", [0.5, 0.8, 0.9, 0.95, 0.99], 0.95)
eps_decay = st.sidebar.select_slider("ε decay per episode", [0.99, 0.995, 0.999, 0.9995], 0.999)
episodes = st.sidebar.slider("Training episodes", 1000, 30000, 10000, 1000)
seed = st.sidebar.number_input("Seed", 0, 9999, 42)
if st.sidebar.button("▶ Train new agent", type="primary"):
    bar = st.sidebar.progress(0.0, text="Training...")
    ag, rows = train(episodes, seed=int(seed), alpha=alpha, gamma=gamma,
                     epsilon_decay=eps_decay, tag="_app", save=False,
                     on_progress=lambda e, n: bar.progress(e / n, text=f"Episode {e}/{n}"))
    bar.empty()
    st.session_state.agent, st.session_state.rows = ag, rows
    st.session_state.source = f"trained now: α={alpha}, γ={gamma}, {episodes} episodes"
st.sidebar.info(f"Agent: {st.session_state.source}")
agent = st.session_state.agent

st.title("SmartTaxi RL — a taxi that learns with Q-Learning")
t_learn, t_demo, t_eval, t_math = st.tabs(["📈 Learning", "🚕 Watch the agent", "⚖️ vs random", "🧮 Q-update calculator"])

# ---------- learning ----------
with t_learn:
    rows = st.session_state.rows
    if rows is None:
        csv = Path(__file__).parent / "results" / "training_results.csv"
        if csv.exists() and st.session_state.source.startswith("pre-trained"):
            df = pd.read_csv(csv)
            st.caption("Showing the training log of the pre-trained model. Press **Train new agent** to run your own.")
        else:
            df = None
    else:
        df = pd.DataFrame(rows)
    if df is None:
        st.info("Press **Train new agent** in the sidebar.")
    else:
        c1, c2, c3 = st.columns(3)
        last = df.tail(200)
        c1.metric("Success (last 200 episodes)", f"{last.success.mean():.0%}")
        c2.metric("Avg reward (last 200)", f"{last.reward.mean():.1f}")
        c3.metric("Final ε", f"{df.epsilon.iloc[-1]:.3f}")
        f1, ax1 = plt.subplots(figsize=(6, 3.4))
        ax1.plot(smooth(df.reward), color=BLUE); ax1.set_title("Average reward (window 100)", loc="left")
        ax1.set_xlabel("episode"); ax1.spines[["top", "right"]].set_visible(False); ax1.grid(alpha=.25)
        f2, ax2 = plt.subplots(figsize=(6, 3.4))
        ax2.plot(smooth(df.success) * 100, color=BLUE)
        ax3 = ax2.twinx(); ax3.plot(df.epsilon, color=ORANGE); ax3.set_ylabel("ε")
        ax2.set_title("Success % (blue) and ε (orange)", loc="left"); ax2.set_xlabel("episode")
        ax2.spines[["top"]].set_visible(False); ax2.grid(alpha=.25)
        a, b = st.columns(2); a.pyplot(f1); b.pyplot(f2)
        f3, ax4 = plt.subplots(figsize=(12, 3))
        ax4.plot(df.episode, df.q_tracked, color=BLUE)
        ax4.set_title("How one Q-value changes: Q(taxi at P0, passenger P0→D0, Pickup)", loc="left")
        ax4.set_xlabel("episode"); ax4.spines[["top", "right"]].set_visible(False); ax4.grid(alpha=.25)
        st.pyplot(f3)
        st.caption("The Q-value starts at 0 and climbs to the true discounted return (≈87.1 for this state) once the agent has found the +100 delivery reward.")

# ---------- demo ----------
with t_demo:
    left, right = st.columns([1, 1])
    with left:
        c1, c2, c3 = st.columns(3)
        pk = c1.selectbox("Pickup", range(4), format_func=lambda i: f"P{i} {city.PICKUP_POINTS[i]}")
        ds = c2.selectbox("Destination", range(4), format_func=lambda i: f"D{i} {city.DESTINATIONS[i]}")
        sx = c3.number_input("Start x", 0, 9, 4); sy = c3.number_input("Start y", 0, 9, 5)
        start = (int(sx), int(sy))
        if not city.is_free(*start):
            st.error("Start cell is an obstacle.")
            st.stop()
        e2 = SmartTaxiEnv()
        s = e2.reset(pickup=pk, dest=ds, start=start)
        path, states, acts, rewards, onb = [e2.taxi], [s], [], [], [0]
        while not e2.done:
            a = agent.choose_action(s, explore=False)
            s, r, *_ = e2.step(a)
            path.append(e2.taxi); states.append(s); acts.append(a); rewards.append(r); onb.append(e2.onboard)
        k = st.slider("Step", 0, len(path) - 1, len(path) - 1)
        st.write(f"**Result:** {'✅ delivered' if e2.success else '❌ not delivered'} in {e2.steps} steps · "
                 f"total reward {sum(rewards):.0f} · wall hits {e2.collisions}")
        st.pyplot(draw_map(path, k, pk, ds, bool(onb[k])))
    with right:
        st.subheader(f"Step {k}")
        q = agent.q_table[states[k]]
        x, y, p, d, b = env.decode(states[k])
        st.write(f"State tuple `(x={x}, y={y}, p={p}, d={d}, b={b})` → table row **{states[k]}**")
        qdf = pd.DataFrame({"action": env.ACTION_NAMES, "Q(s,a)": q.round(2)})
        qdf["chosen"] = ["◀" if (k < len(acts) and i == acts[k]) else "" for i in range(6)]
        st.dataframe(qdf, hide_index=True, width="stretch")
        if k < len(acts):
            st.write(f"Action taken: **{env.ACTION_NAMES[acts[k]]}** (largest Q) → reward {rewards[k]}")
        st.caption("In greedy mode (no exploration) the agent always picks the action with the largest Q in the current row.")

# ---------- evaluation ----------
with t_eval:
    n = st.slider("Number of test tasks", 50, 500, 200, 50)
    if st.button("Run comparison"):
        ev = SmartTaxiEnv()
        rnd = np.random.default_rng(0)
        res = {"Random": [], "Q-Learning": []}
        for i in range(n):
            for name, pol in (("Random", lambda s: int(rnd.integers(6))),
                              ("Q-Learning", lambda s: agent.choose_action(s, explore=False))):
                tot, info = run_episode(ev, 10_000 + i, pol)
                res[name].append((info["success"], info["steps"], tot, info["collisions"]))
        table = pd.DataFrame({k: {"Success rate": np.mean([r[0] for r in v]),
                                  "Avg steps": np.mean([r[1] for r in v]),
                                  "Avg reward": np.mean([r[2] for r in v]),
                                  "Avg wall hits": np.mean([r[3] for r in v])} for k, v in res.items()}).T
        st.dataframe(table.style.format({"Success rate": "{:.1%}", "Avg steps": "{:.1f}",
                                         "Avg reward": "{:.1f}", "Avg wall hits": "{:.2f}"}), width="stretch")
        st.bar_chart(table[["Avg steps"]])
        st.caption("Both agents get identical tasks (same seed per task). Q-Learning is evaluated without exploration.")

# ---------- calculator ----------
with t_math:
    st.latex(r"Q(s,a) \leftarrow Q(s,a) + \alpha\,[\,r + \gamma \max_{a'} Q(s',a') - Q(s,a)\,]")
    c1, c2, c3 = st.columns(3)
    q_old = c1.number_input("Q(s,a) now", value=0.0)
    r = c2.number_input("reward r", value=14.0)
    q_next = c3.number_input("max Q(s',·)", value=20.0)
    c4, c5, c6 = st.columns(3)
    al = c4.number_input("α", 0.0, 1.0, 0.1, 0.01)
    ga = c5.number_input("γ", 0.0, 1.0, 0.95, 0.01)
    term = c6.checkbox("terminal (delivered)")
    target = r + (0 if term else ga * q_next)
    td = target - q_old
    new = q_old + al * td
    st.markdown(f"**Target** = r + γ·max Q(s′) = {r} + {0 if term else ga}·{q_next} = **{target:.3f}**  \n"
                f"**TD error** = {target:.3f} − {q_old:.3f} = **{td:.3f}**  \n"
                f"**New Q** = {q_old:.3f} + {al}·{td:.3f} = **{new:.3f}**")
    k_visits = st.slider("Repeat the same update n times (target fixed)", 1, 50, 10)
    qs = [q_old]
    for _ in range(k_visits):
        qs.append(qs[-1] + al * (target - qs[-1]))
    st.line_chart(pd.DataFrame({"Q": qs}))
