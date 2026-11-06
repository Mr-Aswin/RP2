CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --sf-bg: #0a1020;
        --sf-panel: #111a2c;
        --sf-panel-soft: #151f33;
        --sf-border: rgba(148, 163, 184, 0.13);
        --sf-text: #f1f5fb;
        --sf-muted: #93a2b9;
        --sf-purple: #7562f6;
        --sf-green: #35d49a;
        --sf-red: #ff657a;
        --sf-gold: #f5ca55;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(52, 94, 171, 0.19), transparent 34rem),
            radial-gradient(ellipse at 92% 20%, rgba(117, 98, 246, 0.14), transparent 32rem),
            var(--sf-bg);
        color: var(--sf-text);
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1420px;
        padding: 2.8rem 2rem 3.5rem;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--sf-border) !important;
        border-radius: 20px !important;
        background: linear-gradient(145deg, rgba(20, 30, 49, 0.96), rgba(15, 23, 39, 0.96)) !important;
        box-shadow: 0 22px 55px rgba(0, 0, 0, 0.20);
    }

    .sf-hero {
        margin: 0 0 1.7rem;
        text-align: center;
    }

    .sf-hero h1 {
        margin: 0;
        color: var(--sf-gold);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 5vw, 3.3rem);
        font-weight: 700;
        letter-spacing: -0.055em;
        line-height: 1.08;
        text-shadow: 0 0 34px rgba(245, 202, 85, 0.16);
    }

    .sf-hero p {
        margin: 0.75rem 0 1.25rem;
        color: var(--sf-muted);
        font-size: 0.98rem;
    }

    .sf-badges {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.65rem;
    }

    .sf-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 0.88rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 999px;
        background: rgba(17, 26, 44, 0.78);
        color: #dce5f2;
        font-size: 0.78rem;
        font-weight: 650;
    }

    .sf-check { color: var(--sf-green); font-size: 0.95rem; }

    .sf-browserbar {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        min-height: 44px;
        margin: -0.5rem 0 1.25rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid var(--sf-border);
    }

    .sf-browser-dot { width: 9px; height: 9px; border-radius: 50%; }
    .sf-browser-dot.red { background: #ff657a; }
    .sf-browser-dot.gold { background: #f5bd4f; }
    .sf-browser-dot.green { background: #35d49a; }
    .sf-browser-address {
        margin: 0 auto;
        padding: 0.4rem 2rem;
        border-radius: 7px;
        background: rgba(7, 13, 25, 0.5);
        color: #78889f;
        font-size: 0.74rem;
    }

    .sf-panel-heading {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0 0 0.35rem;
        color: #e7edf7;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 650;
    }

    .sf-panel-icon { color: #a99bff; font-size: 1.15rem; }
    .sf-panel-caption { margin: 0 0 1.2rem; color: var(--sf-muted); font-size: 0.82rem; }

    [data-testid="stTextArea"] label {
        color: #cbd5e1 !important;
        font-size: 0.82rem !important;
        font-weight: 650 !important;
    }

    [data-testid="stTextArea"] textarea {
        min-height: 275px;
        border: 1px solid rgba(148, 163, 184, 0.13) !important;
        border-radius: 13px !important;
        background: #0a1120 !important;
        color: var(--sf-text) !important;
        font-family: 'DM Sans', sans-serif !important;
        line-height: 1.65 !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(117, 98, 246, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(117, 98, 246, 0.13) !important;
    }

    .sf-count-row {
        display: flex;
        justify-content: space-between;
        margin: 0.55rem 0 0.85rem;
        color: #718198;
        font-size: 0.74rem;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 46px;
        border: 0 !important;
        border-radius: 11px !important;
        background: linear-gradient(110deg, #6354ed, #7963f8) !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 24px rgba(99, 84, 237, 0.22);
        transition: transform 150ms ease, filter 150ms ease;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        filter: brightness(1.09);
    }

    [data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div:last-child [data-testid="stFormSubmitButton"] button {
        border: 1px solid var(--sf-border) !important;
        background: rgba(30, 41, 59, 0.58) !important;
        color: #d1d9e6 !important;
        box-shadow: none;
    }

    .sf-result-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
    }

    .sf-result-label {
        margin: 0 0 0.38rem;
        color: var(--sf-muted);
        font-size: 0.69rem;
        font-weight: 750;
        letter-spacing: 0.11em;
        text-transform: uppercase;
    }

    .sf-result-sentiment {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.04em;
    }

    .sf-result-sentiment.positive { color: var(--sf-green); }
    .sf-result-sentiment.negative { color: var(--sf-red); }
    .sf-result-icon { color: #9aa9be; font-size: 1.3rem; }

    .sf-gauge-wrap {
        display: grid;
        justify-items: center;
        margin: 1.3rem 0 1.2rem;
    }

    .sf-gauge {
        display: grid;
        width: 164px;
        aspect-ratio: 1;
        place-items: center;
        border-radius: 50%;
        background: conic-gradient(var(--gauge-color) var(--gauge-value), rgba(71, 85, 105, 0.38) 0);
        transform: rotate(-45deg);
    }

    .sf-gauge-inner {
        display: grid;
        width: 136px;
        height: 136px;
        place-content: center;
        border-radius: 50%;
        background: #121b2d;
        text-align: center;
        transform: rotate(45deg);
    }

    .sf-gauge-value {
        color: var(--sf-text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.06em;
        line-height: 1;
    }

    .sf-gauge-caption {
        margin-top: 0.38rem;
        color: var(--sf-muted);
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.1em;
    }

    .sf-probability-list { display: grid; gap: 0.9rem; }
    .sf-probability-head {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.4rem;
        color: #c5cfdd;
        font-size: 0.79rem;
    }

    .sf-probability-value { color: #f1f5fb; font-weight: 700; }
    .sf-progress { height: 7px; overflow: hidden; border-radius: 99px; background: rgba(71, 85, 105, 0.35); }
    .sf-progress-fill { height: 100%; border-radius: inherit; }
    .sf-progress-fill.positive { background: linear-gradient(90deg, #20b981, #50e0a9); }
    .sf-progress-fill.negative { background: linear-gradient(90deg, #ed536d, #ff8190); }

    .sf-empty-state {
        display: grid;
        min-height: 320px;
        align-content: center;
        justify-items: center;
        padding: 1.5rem;
        text-align: center;
    }

    .sf-empty-icon {
        display: grid;
        width: 58px;
        height: 58px;
        place-items: center;
        margin-bottom: 1rem;
        border: 1px solid rgba(117, 98, 246, 0.25);
        border-radius: 18px;
        background: rgba(117, 98, 246, 0.1);
        color: #b7adff;
        font-size: 1.5rem;
    }

    .sf-empty-title { margin: 0; color: #dfe7f3; font-weight: 700; }
    .sf-empty-copy { max-width: 270px; margin: 0.55rem 0 0; color: #8493a9; font-size: 0.82rem; line-height: 1.6; }

    .sf-footnote { margin: 1rem 0 0; color: #718198; font-size: 0.72rem; line-height: 1.5; }

    @media (max-width: 768px) {
        .block-container { padding: 1.8rem 1rem 2.5rem; }
        [data-testid="stTextArea"] textarea { min-height: 210px; }
        .sf-empty-state { min-height: 220px; }
    }
</style>
"""
