CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at top left, rgba(77, 103, 255, 0.18), transparent 28%),
                    radial-gradient(circle at bottom right, rgba(168, 85, 247, 0.14), transparent 25%),
                    #07111f;
        color: #edf3ff;
        font-family: 'Inter', sans-serif;
    }

    .sentimentforge-shell {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1.4rem 0 3rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.75rem;
        padding: 0.9rem 1.1rem;
        background: rgba(12, 21, 34, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.24);
    }

    .brand-group {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        font-weight: 800;
        box-shadow: 0 14px 22px rgba(59, 130, 246, 0.35);
    }

    .project-title {
        margin: 0;
        font-size: clamp(1.7rem, 2.1vw, 2.3rem);
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .project-tagline {
        margin: 0.2rem 0 0;
        font-size: 0.95rem;
        color: #a7b7d1;
    }

    .header-badges {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 0.65rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.45rem 0.82rem;
        border-radius: 999px;
        border: 1px solid rgba(125, 211, 252, 0.24);
        background: rgba(14, 116, 144, 0.14);
        color: #d7e9ff;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .page-card {
        background: rgba(8, 17, 31, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 22px;
        padding: 1.3rem;
        box-shadow: 0 16px 32px rgba(2, 6, 23, 0.25);
    }

    .result-card {
        background: linear-gradient(180deg, rgba(10, 18, 33, 0.88), rgba(15, 23, 42, 0.66));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 22px;
        padding: 1.3rem 1.25rem;
        margin-top: 1rem;
    }

    .result-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.55rem 0.9rem;
        border-radius: 999px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .result-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 0.9rem;
        margin-top: 0.7rem;
    }

    .metric-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 0.85rem 1rem;
    }

    .metric-label {
        display: block;
        color: #a6b7d1;
        font-size: 0.75rem;
        margin-bottom: 0.38rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        font-size: 1.45rem;
        font-weight: 750;
        letter-spacing: -0.05em;
    }

    .note {
        margin-top: 1rem;
        color: #a8b5c9;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    .analysis-form {
        margin-top: 1rem;
    }

    .count-row {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
        color: #9bb0ca;
        font-size: 0.78rem;
    }

    .secondary-button {
        background: rgba(30, 41, 59, 0.9);
        color: #e2e8f0 !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
    }

    .primary-button {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white !important;
        border: none !important;
        box-shadow: 0 12px 28px rgba(59, 130, 246, 0.28);
    }

    @media (max-width: 768px) {
        .topbar {
            flex-direction: column;
            align-items: flex-start;
        }

        .header-badges {
            justify-content: flex-start;
        }
    }
</style>
"""
