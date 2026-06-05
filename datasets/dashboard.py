import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st
from collections import Counter
import re
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkillScout Nusantara Dashboard | Platform Pencari Kerja Berbasis AI Untuk Masyarakat Indonesia",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Style ───────────────────────────────────────────────────────────────
DARK_BG   = '#0f0f1a'
PANEL_BG  = '#1a1a2e'
BORDER    = '#444466'
TEXT      = '#e0e0ff'
MUTED     = '#aaaacc'
ACCENT    = '#facc15'

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor':   PANEL_BG,
    'axes.edgecolor':   BORDER,
    'axes.labelcolor':  TEXT,
    'xtick.color':      MUTED,
    'ytick.color':      MUTED,
    'text.color':       TEXT,
    'grid.color':       '#2a2a4a',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
    'font.family':      'DejaVu Sans',
})

PALETTE = ['#7b5ea7','#a78bfa','#60a5fa','#34d399','#f472b6',
           '#fb923c','#facc15','#38bdf8','#a3e635','#f87171']

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f0f1a; color: #e0e0ff; }
    .main .block-container { background-color: #0f0f1a; padding-top: 1rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12122a;
        border-right: 1px solid #444466;
    }
    section[data-testid="stSidebar"] * { color: #e0e0ff !important; }
    .stSelectbox label, .stMultiSelect label { color: #a78bfa !important; font-weight: 600; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #444466;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #a78bfa !important; font-size: 2rem !important; }
    [data-testid="stMetricLabel"] { color: #aaaacc !important; }

    /* Section headers */
    .section-title {
        color: #a78bfa;
        font-size: 1.3rem;
        font-weight: 700;
        border-bottom: 2px solid #7b5ea7;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }
    .sub-header {
        color: #60a5fa;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #12122a; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #aaaacc !important; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background-color: #7b5ea7 !important; color: white !important; }

    /* Divider */
    hr { border-color: #2a2a4a; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f0f1a; }
    ::-webkit-scrollbar-thumb { background: #7b5ea7; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def parse_skills(series):
    all_skills = []
    for s in series.dropna():
        skills = [x.strip().lower() for x in str(s).split(',') if x.strip()]
        all_skills.extend(skills)
    return Counter(all_skills)

def user_skills_set(row):
    skills = set()
    for col in ['extracted_user_skills', 'extracted_skills_structured']:
        val = row.get(col, '')
        if pd.notna(val) and str(val).strip() not in ('', 'unspecified', 'not specified'):
            skills.update([x.strip().lower() for x in str(val).split(',') if x.strip()])
    return skills

@st.cache_data
def load_data():
    jm = pd.read_csv('JobMarket_Preprocessed.csv')
    cv = pd.read_csv('cv_processed.csv')
    return jm, cv

@st.cache_data
def build_role_skill_pool(_jm):
    pool = {}
    for role, grp in _jm.groupby('role_category'):
        skills = set()
        for s in grp['extracted_skills'].dropna():
            skills.update([x.strip().lower() for x in str(s).split(',') if x.strip()])
        pool[role] = skills
    return pool

@st.cache_data
def build_match_df(_jm, _cv):
    pool = build_role_skill_pool(_jm)
    roles = list(pool.keys())
    records = []
    for _, user in _cv.iterrows():
        uset = user_skills_set(user)
        for role in roles:
            p = pool[role]
            matched = len(uset & p)
            score = matched / len(p) if len(p) > 0 else 0
            records.append({'user_id': user['user_id'], 'role': role,
                            'match_score': score, 'matched_skills': matched,
                            'pool_size': len(p)})
    return pd.DataFrame(records)

def set_dark_spines(ax):
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.tick_params(colors=MUTED)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

try:
    jm, cv = load_data()
    data_ok = True
except FileNotFoundError:
    data_ok = False

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 💼 SkillScout Nusantara Dashboard")
    st.markdown("---")

    if data_ok:
        st.markdown("### 🔍 Filter")
        all_roles = sorted(jm['role_category'].dropna().unique().tolist())
        selected_roles = st.multiselect(
            "Role Category",
            options=all_roles,
            default=all_roles,
            help="Filter berdasarkan kategori pekerjaan"
        )

        exp_levels = sorted(jm['experience_level'].fillna('unspecified').unique().tolist())
        selected_exp = st.multiselect(
            "Experience Level",
            options=exp_levels,
            default=exp_levels
        )

        top_n_skills = st.slider("Top N Skills ditampilkan", 10, 30, 20)
        gap_top_n    = st.slider("Top N Skill Gap ditampilkan", 5, 20, 15)

        st.markdown("---")
        st.markdown(f"**📊 Total Lowongan:** `{len(jm):,}`")
        st.markdown(f"**👤 Total Users (CV):** `{len(cv):,}`")
        st.markdown(f"**🗂️ Role Categories:** `{jm['role_category'].nunique()}`")
    else:
        st.warning("⚠️ Data tidak ditemukan.\nLetakkan file berikut di direktori yang sama:\n- `JobMarket_Preprocessed.csv`\n- `cv_processed.csv`")

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
     border-radius: 16px; padding: 28px 36px; margin-bottom: 24px;
     border: 1px solid #444466;">
    <h1 style="color: #a78bfa; margin: 0 0 6px 0; font-size: 2rem;">
        💼 SkillScout Nusantara Dashboard
    </h1>
    <p style="color: #aaaacc; margin: 0; font-size: 1rem;">
        Analisis kecocokan skill users terhadap pasar kerja lokal · 
        Skill gap & rekomendasi pekerjaan
    </p>
</div>
""", unsafe_allow_html=True)

if not data_ok:
    st.error("❌ File data tidak ditemukan. Pastikan `JobMarket_Preprocessed.csv` dan `cv_processed.csv` ada di direktori yang sama dengan `dashboard.py`.")
    st.stop()

# ── Apply filters ──────────────────────────────────────────────────────────────
jm_f = jm[
    jm['role_category'].isin(selected_roles) &
    jm['experience_level'].fillna('unspecified').isin(selected_exp)
]

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_eda, tab_bq1, tab_bq2, tab_bq3 = st.tabs([
    "📊 EDA Umum",
    "🎯 BQ1 · Role Match",
    "🧩 BQ2 · Skill Gap",
    "🏆 BQ3 · Top Jobs"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDA UMUM
# ══════════════════════════════════════════════════════════════════════════════

with tab_eda:
    st.markdown('<p class="section-title">📊 Exploratory Data Analysis — Job Market</p>', unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lowongan", f"{len(jm_f):,}")
    c2.metric("Role Categories", jm_f['role_category'].nunique())
    c3.metric("Avg Skills/Lowongan",
              f"{jm_f['extracted_job_skills_count'].mean():.1f}" if 'extracted_job_skills_count' in jm_f.columns else "–")
    c4.metric("Total CV Users", f"{len(cv):,}")

    st.markdown("---")

    # Row 1: Bar + Pie
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="sub-header">Distribusi Kategori Pekerjaan</p>', unsafe_allow_html=True)
        role_counts = jm_f['role_category'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(DARK_BG)
        bars = ax.barh(role_counts.index, role_counts.values,
                       color=PALETTE[:len(role_counts)], edgecolor=BORDER, linewidth=0.7)
        set_dark_spines(ax)
        ax.set_title('Distribusi Kategori Pekerjaan di Pasar Lokal', fontweight='bold')
        ax.set_xlabel('Jumlah Lowongan')
        ax.invert_yaxis()
        for bar, val in zip(bars, role_counts.values):
            ax.text(val + max(role_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=8, color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.markdown('<p class="sub-header">Proporsi Role (Pie Chart)</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(DARK_BG)
        wedges, texts, autotexts = ax.pie(
            role_counts.values, labels=role_counts.index,
            colors=PALETTE[:len(role_counts)], autopct='%1.1f%%',
            startangle=140, pctdistance=0.82,
            textprops={'fontsize': 8, 'color': TEXT}
        )
        for at in autotexts:
            at.set_color('white'); at.set_fontweight('bold')
        ax.set_title('Proporsi Kategori Pekerjaan', fontweight='bold', color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Row 2: Experience Level + Skills per Lowongan
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown('<p class="sub-header">Distribusi Experience Level</p>', unsafe_allow_html=True)
        exp_counts = jm_f['experience_level'].fillna('unspecified').value_counts()
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor(DARK_BG)
        bars = ax.bar(exp_counts.index, exp_counts.values,
                      color=['#7b5ea7','#60a5fa','#34d399'][:len(exp_counts)],
                      edgecolor=BORDER, linewidth=0.8)
        set_dark_spines(ax)
        ax.set_title('Distribusi Level Pengalaman — Job Market', fontweight='bold')
        ax.set_ylabel('Jumlah Lowongan')
        for bar, val in zip(bars, exp_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(exp_counts.values)*0.01,
                    f'{val:,}', ha='center', fontsize=9, fontweight='bold', color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r2:
        if 'extracted_job_skills_count' in jm_f.columns:
            st.markdown('<p class="sub-header">Distribusi Jumlah Skill per Lowongan</p>', unsafe_allow_html=True)
            data_clean = jm_f['extracted_job_skills_count'].dropna()
            min_val = int(data_clean.min()); max_val = int(data_clean.max())
            bins_custom = np.arange(min_val - 0.5, max_val + 1.5, 1)
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(DARK_BG)
            ax.hist(data_clean, bins=bins_custom, color='#7b5ea7',
                    edgecolor='#a78bfa', linewidth=0.7, rwidth=0.8)
            ax.set_xticks(np.arange(min_val, max_val + 1))
            ax.axvline(data_clean.mean(), color=ACCENT, linestyle='--',
                       linewidth=2, label=f"Mean: {data_clean.mean():.1f}")
            set_dark_spines(ax)
            ax.set_title('Distribusi Jumlah Skill per Lowongan', fontweight='bold')
            ax.set_xlabel('Jumlah Skill'); ax.set_ylabel('Frekuensi')
            legend = ax.legend(facecolor=DARK_BG, edgecolor='#a78bfa')
            for t in legend.get_texts(): t.set_color('white')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    # Top N Skills
    st.markdown("---")
    st.markdown(f'<p class="sub-header">Top {top_n_skills} Skills Paling Banyak Dibutuhkan</p>', unsafe_allow_html=True)
    jm_skill_counts = parse_skills(jm_f['extracted_skills'])
    top_jm = pd.DataFrame(jm_skill_counts.most_common(top_n_skills), columns=['skill', 'count'])
    fig, ax = plt.subplots(figsize=(13, max(6, top_n_skills * 0.42)))
    fig.patch.set_facecolor(DARK_BG)
    cmap = plt.cm.get_cmap('cool', top_n_skills)
    colors = [cmap(i / top_n_skills) for i in range(top_n_skills)]
    bars = ax.barh(top_jm['skill'], top_jm['count'], color=colors)
    set_dark_spines(ax)
    ax.set_title(f'Top {top_n_skills} Skills Paling Banyak Dibutuhkan Pasar Kerja', fontweight='bold')
    ax.set_xlabel('Frekuensi Kemunculan')
    ax.invert_yaxis()
    for bar, val in zip(bars, top_jm['count']):
        ax.text(val + max(top_jm['count']) * 0.005, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=8, color=TEXT)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BQ1
# ══════════════════════════════════════════════════════════════════════════════

with tab_bq1:
    st.markdown('<p class="section-title">🎯 BQ1 · Role dengan Kecocokan Tertinggi</p>', unsafe_allow_html=True)
    st.info("**Business Question:** Pekerjaan apa yang memiliki tingkat kecocokan tertinggi dengan pengalaman user saat ini?")

    with st.spinner("Menghitung match score... (mungkin sebentar)"):
        role_skill_pool = build_role_skill_pool(jm)
        match_df = build_match_df(jm, cv)

    avg_match = (match_df.groupby('role')['match_score']
                 .agg(['mean', 'median', 'std'])
                 .round(4)
                 .sort_values('mean', ascending=False)
                 .reset_index())
    avg_match.columns = ['role_category', 'avg_match_score', 'median_score', 'std_score']
    avg_match['avg_match_pct'] = (avg_match['avg_match_score'] * 100).round(2)

    best_role = avg_match.iloc[0]

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("🥇 Best Match Role", best_role['role_category'])
    c2.metric("Avg Match Score", f"{best_role['avg_match_pct']:.2f}%")
    c3.metric("Median Score", f"{best_role['median_score']*100:.2f}%")

    st.markdown("---")

    # Bar chart + Boxplot side by side
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="sub-header">Rata-rata Match Score per Role</p>', unsafe_allow_html=True)
        grand_mean = avg_match['avg_match_pct'].mean()
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(DARK_BG)
        colors_bar = [PALETTE[i % len(PALETTE)] for i in range(len(avg_match))]
        bars = ax.barh(avg_match['role_category'], avg_match['avg_match_pct'],
                       color=colors_bar, edgecolor='#333355', linewidth=0.7)
        ax.axvline(grand_mean, color=ACCENT, linestyle='--', linewidth=1.5,
                   label=f'Grand mean: {grand_mean:.1f}%')
        set_dark_spines(ax)
        ax.set_title('Rata-rata Kecocokan User terhadap\nSetiap Role (Semua User)', fontweight='bold')
        ax.set_xlabel('Avg Match Score (%)')
        ax.gca().invert_yaxis() if hasattr(ax, 'gca') else ax.invert_yaxis()
        ax.invert_yaxis()
        legend = ax.legend(fontsize=9, facecolor=DARK_BG, edgecolor=BORDER)
        for t in legend.get_texts(): t.set_color('white')
        for bar, val in zip(bars, avg_match['avg_match_pct']):
            ax.text(val + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=9, fontweight='bold', color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.markdown('<p class="sub-header">Distribusi Match Score (Box Plot)</p>', unsafe_allow_html=True)
        role_order = avg_match['role_category'].tolist()
        data_box = [match_df[match_df['role'] == r]['match_score'] * 100 for r in role_order]
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(DARK_BG)
        bp = ax.boxplot(data_box, vert=False, patch_artist=True,
                        medianprops=dict(color=ACCENT, linewidth=2))
        colors_bar = [PALETTE[i % len(PALETTE)] for i in range(len(role_order))]
        for patch, color in zip(bp['boxes'], colors_bar):
            patch.set_facecolor(color); patch.set_alpha(0.7)
        for element in ['whiskers', 'caps', 'fliers']:
            plt.setp(bp[element], color=MUTED)
        ax.set_yticks(range(1, len(role_order) + 1))
        ax.set_yticklabels(role_order, fontsize=8)
        set_dark_spines(ax)
        ax.set_title('Distribusi Match Score per Role\n(Box Plot)', fontweight='bold')
        ax.set_xlabel('Match Score (%)')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Users above threshold
    st.markdown("---")
    st.markdown('<p class="sub-header">% User dengan Match Score ≥ 10% per Role</p>', unsafe_allow_html=True)
    threshold = 0.10
    top_roles_df = (match_df[match_df['match_score'] >= threshold]
                    .groupby('role')['user_id'].count()
                    .sort_values(ascending=False).reset_index())
    top_roles_df.columns = ['role_category', 'users_above_threshold']
    top_roles_df['pct_of_users'] = (top_roles_df['users_above_threshold'] / len(cv) * 100).round(2)

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(DARK_BG)
    bars = ax.bar(top_roles_df['role_category'], top_roles_df['pct_of_users'],
                  color=[PALETTE[i % len(PALETTE)] for i in range(len(top_roles_df))],
                  edgecolor='#333355', linewidth=0.7)
    set_dark_spines(ax)
    ax.set_title('% User dengan Match Score ≥ 10% per Role', fontweight='bold')
    ax.set_ylabel('% User'); ax.set_xlabel('Role Category')
    plt.xticks(rotation=25, ha='right', fontsize=9)
    for bar, val in zip(bars, top_roles_df['pct_of_users']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.1f}%', ha='center', fontsize=9, fontweight='bold', color=TEXT)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Summary table
    st.markdown("---")
    st.markdown('<p class="sub-header">📋 Tabel Ringkasan BQ1</p>', unsafe_allow_html=True)
    display_df = avg_match[['role_category', 'avg_match_pct', 'median_score', 'std_score']].copy()
    display_df['median_pct'] = (display_df['median_score'] * 100).round(2)
    display_df['std_pct'] = (display_df['std_score'] * 100).round(2)
    st.dataframe(
        display_df[['role_category', 'avg_match_pct', 'median_pct', 'std_pct']]
        .rename(columns={
            'role_category': 'Role Category',
            'avg_match_pct': 'Avg Match (%)',
            'median_pct': 'Median (%)',
            'std_pct': 'Std Dev (%)'
        }),
        use_container_width=True, hide_index=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BQ2
# ══════════════════════════════════════════════════════════════════════════════

with tab_bq2:
    st.markdown('<p class="section-title">🧩 BQ2 · Skill Gap Krusial</p>', unsafe_allow_html=True)
    st.info("**Business Question:** Keterampilan inti apa yang belum dimiliki user namun krusial untuk posisi target?")

    # Re-use avg_match from BQ1 (already computed above in tab_bq1; recompute if not available)
    try:
        target_role = avg_match.iloc[0]['role_category']
    except NameError:
        role_skill_pool = build_role_skill_pool(jm)
        match_df = build_match_df(jm, cv)
        avg_match = (match_df.groupby('role')['match_score']
                     .agg(['mean', 'median', 'std']).round(4)
                     .sort_values('mean', ascending=False).reset_index())
        avg_match.columns = ['role_category', 'avg_match_score', 'median_score', 'std_score']
        avg_match['avg_match_pct'] = (avg_match['avg_match_score'] * 100).round(2)
        target_role = avg_match.iloc[0]['role_category']

    target_pool = role_skill_pool[target_role]

    # Allow user to pick target role
    chosen_role = st.selectbox(
        "Pilih Role Target untuk Analisis Skill Gap:",
        options=avg_match['role_category'].tolist(),
        index=0
    )
    target_pool = role_skill_pool[chosen_role]

    # Build gap_df
    @st.cache_data
    def build_gap_df(chosen_role, _cv, _jm, _role_skill_pool):
        pool = _role_skill_pool[chosen_role]
        gap_records = []
        for _, user in _cv.iterrows():
            uset = user_skills_set(user)
            gap = pool - uset
            gap_records.append({'user_id': user['user_id'], 'gap_skills': gap})
        gap_counter = Counter()
        for r in gap_records:
            gap_counter.update(r['gap_skills'])
        gdf = pd.DataFrame(gap_counter.most_common(), columns=['skill', 'users_missing'])
        gdf['pct_users_missing'] = (gdf['users_missing'] / len(_cv) * 100).round(2)
        jm_target = _jm[_jm['role_category'] == chosen_role]
        target_freq = parse_skills(jm_target['extracted_skills'])
        gdf['job_freq'] = gdf['skill'].map(lambda s: target_freq.get(s, 0))
        gdf['crucial_score'] = (
            gdf['pct_users_missing'] / 100 * 0.5 +
            gdf['job_freq'] / (gdf['job_freq'].max() + 1e-9) * 0.5
        )
        return gdf.sort_values('crucial_score', ascending=False).reset_index(drop=True)

    with st.spinner("Menghitung skill gap..."):
        gap_df = build_gap_df(chosen_role, cv, jm, role_skill_pool)

    top_gap = gap_df.head(gap_top_n)

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("Role Target", chosen_role)
    c2.metric("Unique Skill Pool", len(target_pool))
    c3.metric("Total Skill Gap Unik", len(gap_df))

    st.markdown("---")

    # Bar + Scatter
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f'<p class="sub-header">Top {gap_top_n} Skill Gap · % User Belum Memiliki</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, max(5, gap_top_n * 0.4)))
        fig.patch.set_facecolor(DARK_BG)
        cmap2 = plt.cm.get_cmap('plasma', gap_top_n)
        col2 = [cmap2(i / gap_top_n) for i in range(gap_top_n)]
        bars = ax.barh(top_gap['skill'], top_gap['pct_users_missing'],
                       color=col2, edgecolor='#333355', linewidth=0.6)
        set_dark_spines(ax)
        ax.set_title(f'Top {gap_top_n} Skill Gap — {chosen_role.title()}\n(% User yang Belum Memiliki)',
                     fontweight='bold', fontsize=11)
        ax.set_xlabel('% User yang Belum Memiliki Skill')
        ax.invert_yaxis()
        for bar, val in zip(bars, top_gap['pct_users_missing']):
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=8, color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.markdown('<p class="sub-header">Krusialitas Skill: Gap vs Job Frequency</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, max(5, gap_top_n * 0.4)))
        fig.patch.set_facecolor(DARK_BG)
        sc = ax.scatter(top_gap['job_freq'], top_gap['pct_users_missing'],
                        s=top_gap['crucial_score'] * 800 + 100,
                        c=top_gap['crucial_score'], cmap='plasma',
                        edgecolors=MUTED, linewidths=0.8, alpha=0.9)
        for _, row in top_gap.iterrows():
            ax.annotate(row['skill'], (row['job_freq'], row['pct_users_missing']),
                        fontsize=7, ha='left', va='bottom', color='#ccccee',
                        xytext=(3, 3), textcoords='offset points')
        set_dark_spines(ax)
        ax.set_title('Krusialitas Skill: Frekuensi di Job vs % User Gap',
                     fontweight='bold', fontsize=11)
        ax.set_xlabel('Frekuensi Kemunculan di Job Posting')
        ax.set_ylabel('% User Belum Punya')
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Crucial Score', color=TEXT)
        cbar.ax.yaxis.set_tick_params(color=MUTED)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Heatmap
    st.markdown("---")
    st.markdown('<p class="sub-header">Heatmap Skill Gap · Top 5 Role × Top 20 Skill</p>', unsafe_allow_html=True)

    @st.cache_data
    def build_heatmap(_cv, _jm, _avg_match, _role_skill_pool):
        top5 = _avg_match.head(5)['role_category'].tolist()
        heat_data = {}
        for role in top5:
            pool = _role_skill_pool[role]
            gap_c = Counter()
            for _, user in _cv.iterrows():
                uset = user_skills_set(user)
                gap_c.update(pool - uset)
            top10 = [s for s, _ in gap_c.most_common(10)]
            heat_data[role] = {s: gap_c[s] / len(_cv) * 100 for s in top10}
        all_skills_heat = []
        for skills in heat_data.values():
            all_skills_heat.extend(skills.keys())
        all_skills_heat = list(dict.fromkeys(all_skills_heat))[:20]
        heat_matrix = pd.DataFrame(
            {role: [heat_data[role].get(s, 0) for s in all_skills_heat] for role in top5},
            index=all_skills_heat
        )
        return heat_matrix

    with st.spinner("Membangun heatmap..."):
        heat_matrix = build_heatmap(cv, jm, avg_match, role_skill_pool)

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor(DARK_BG)
    sns.heatmap(heat_matrix, ax=ax, cmap='RdPu', annot=True, fmt='.0f',
                linewidths=0.4, linecolor=PANEL_BG,
                cbar_kws={'label': '% User Belum Punya Skill'})
    ax.set_title('Heatmap Skill Gap: Top 5 Role × Top 20 Skill yang Belum Dimiliki User (%)',
                 fontsize=12, fontweight='bold', color=TEXT, pad=15)
    ax.set_xlabel('Role Category', color=TEXT)
    ax.set_ylabel('Skill', color=TEXT)
    ax.tick_params(colors=MUTED)
    plt.xticks(rotation=20, ha='right', fontsize=9)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Gap table
    st.markdown("---")
    st.markdown(f'<p class="sub-header">📋 Top 20 Skill Gap — {chosen_role}</p>', unsafe_allow_html=True)
    st.dataframe(
        gap_df.head(20)[['skill', 'users_missing', 'pct_users_missing', 'job_freq', 'crucial_score']]
        .rename(columns={
            'skill': 'Skill', 'users_missing': 'User Belum Punya',
            'pct_users_missing': '% User Gap', 'job_freq': 'Freq di Job', 'crucial_score': 'Crucial Score'
        }),
        use_container_width=True, hide_index=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BQ3
# ══════════════════════════════════════════════════════════════════════════════

with tab_bq3:
    st.markdown('<p class="section-title">🏆 BQ3 · Top 5 Pekerjaan Paling Cocok</p>', unsafe_allow_html=True)
    st.info("**Business Question:** Apa 3–5 pekerjaan teratas yang paling cocok beserta persentase kecocokannya?")

    # Top-5 per user
    try:
        _ = match_df
    except NameError:
        role_skill_pool = build_role_skill_pool(jm)
        match_df = build_match_df(jm, cv)
        avg_match = (match_df.groupby('role')['match_score']
                     .agg(['mean', 'median', 'std']).round(4)
                     .sort_values('mean', ascending=False).reset_index())
        avg_match.columns = ['role_category', 'avg_match_score', 'median_score', 'std_score']
        avg_match['avg_match_pct'] = (avg_match['avg_match_score'] * 100).round(2)

    top5_per_user = (match_df.sort_values(['user_id', 'match_score'], ascending=[True, False])
                     .groupby('user_id').head(5)
                     .assign(rank=lambda d: d.groupby('user_id').cumcount() + 1))

    rank_counts = (top5_per_user.groupby(['role', 'rank'])['user_id']
                   .count().unstack(fill_value=0)
                   .rename(columns={i: f'rank_{i}' for i in range(1, 6)}))
    weights = {f'rank_{i}': 6-i for i in range(1, 6)}
    rank_counts['weighted_score'] = sum(rank_counts.get(col, 0) * w for col, w in weights.items())
    rank_counts = rank_counts.sort_values('weighted_score', ascending=False)

    top1_per_user = top5_per_user[top5_per_user['rank'] == 1]
    top1_avg = (top1_per_user.groupby('role')['match_score']
                .agg(['mean', 'median', 'count']).round(4)
                .sort_values('mean', ascending=False).reset_index())
    top1_avg.columns = ['role_category', 'avg_match_top1', 'median_match_top1', 'user_count_top1']
    top1_avg['avg_match_pct'] = (top1_avg['avg_match_top1'] * 100).round(2)

    top5_display = top1_avg.head(5)
    c_bar = [PALETTE[i] for i in range(5)]

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("🥇 #1 Best Job", top5_display.iloc[0]['role_category'])
    c2.metric("Avg Match (Top-1)", f"{top5_display.iloc[0]['avg_match_pct']:.2f}%")
    c3.metric("Users Pilih Role Ini", f"{int(top5_display.iloc[0]['user_count_top1']):,}")

    st.markdown("---")

    # Grouped bar + Horizontal bar
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="sub-header">Frekuensi Role Masuk sebagai Top-1 s.d. Top-5</p>', unsafe_allow_html=True)
        rank_cols = [c for c in rank_counts.columns if c.startswith('rank_')]
        x = np.arange(len(rank_counts))
        width = 0.15
        rank_colors = ['#7b5ea7', '#60a5fa', '#34d399', '#f472b6', ACCENT]
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor(DARK_BG)
        for i, (col, color) in enumerate(zip(rank_cols, rank_colors)):
            ax.bar(x + i*width, rank_counts[col], width,
                   label=col.replace('_', ' ').title(),
                   color=color, edgecolor='#333355', linewidth=0.6, alpha=0.85)
        ax.set_xticks(x + width*2)
        ax.set_xticklabels(rank_counts.index, rotation=22, ha='right', fontsize=8, color=TEXT)
        set_dark_spines(ax)
        ax.set_title('Frekuensi Role Masuk Top-1 s.d. Top-5\nPilihan User', fontweight='bold')
        ax.set_ylabel('Jumlah User')
        legend = ax.legend(fontsize=8, loc='upper right', facecolor=DARK_BG, edgecolor=BORDER)
        for t in legend.get_texts(): t.set_color('white')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.markdown('<p class="sub-header">Top 5 Role: Avg Match Score saat Menjadi Pilihan Utama</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor(DARK_BG)
        hbars = ax.barh(top5_display['role_category'], top5_display['avg_match_pct'],
                        color=c_bar, edgecolor='#333355', linewidth=0.7)
        set_dark_spines(ax)
        ax.set_title('Top 5 Role: Avg Match Score\nsaat Menjadi Pilihan Utama User', fontweight='bold')
        ax.set_xlabel('Avg Match Score (%)')
        ax.invert_yaxis()
        for bar, val in zip(hbars, top5_display['avg_match_pct']):
            ax.text(val + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}%', va='center', fontsize=10, fontweight='bold', color=TEXT)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Violin + Threshold curve
    col_l2, col_r2 = st.columns(2)
    top5_role_names = top1_avg.head(5)['role_category'].tolist()

    with col_l2:
        st.markdown('<p class="sub-header">Distribusi Match Score — Top 5 Role (Violin)</p>', unsafe_allow_html=True)
        violin_data = []
        valid_roles = []
        for r in top5_role_names:
            d = match_df[match_df['role'] == r]['match_score'] * 100
            if not d.empty:
                violin_data.append(d)
                valid_roles.append(r)
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor(DARK_BG)
        if violin_data:
            parts = ax.violinplot(violin_data, positions=range(1, len(violin_data) + 1), showmedians=True)
            for pc, color in zip(parts['bodies'], c_bar[:len(violin_data)]):
                pc.set_facecolor(color); pc.set_alpha(0.7)
            parts['cmedians'].set_color(ACCENT); parts['cmedians'].set_linewidth(2)
            for pn in ('cbars', 'cmins', 'cmaxes'):
                parts[pn].set_color(TEXT); parts[pn].set_linewidth(1)
            ax.set_xticks(range(1, len(valid_roles) + 1))
            ax.set_xticklabels([r.replace(' / ', '/\n') for r in valid_roles], fontsize=8, color=TEXT)
        set_dark_spines(ax)
        ax.set_title('Distribusi Match Score — Top 5 Role\n(Violin Plot)', fontweight='bold')
        ax.set_ylabel('Match Score (%)')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r2:
        st.markdown('<p class="sub-header">% User Qualified per Threshold</p>', unsafe_allow_html=True)
        thresholds = np.arange(0, 0.81, 0.05)
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor(DARK_BG)
        for i, role in enumerate(top5_role_names):
            scores = match_df[match_df['role'] == role]['match_score'].values
            vals = [(scores >= t).sum() / len(cv) * 100 for t in thresholds]
            ax.plot(thresholds * 100, vals, color=PALETTE[i], linewidth=2.5,
                    label=role, marker='o', markersize=4)
            ax.fill_between(thresholds * 100, vals, alpha=0.1, color=PALETTE[i])
        ax.axvline(30, color=ACCENT, linestyle='--', linewidth=1.5, alpha=0.7, label='Threshold 30%')
        set_dark_spines(ax)
        ax.set_title('% User yang Memenuhi Threshold Match\nScore — Top 5 Role', fontweight='bold')
        ax.set_xlabel('Minimum Match Score (%)'); ax.set_ylabel('% User Qualified')
        ax.set_xlim(0, 80)
        legend = ax.legend(fontsize=8, loc='upper right', facecolor=DARK_BG, edgecolor=BORDER)
        for t in legend.get_texts(): t.set_color('white')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Final summary table
    st.markdown("---")
    st.markdown('<p class="sub-header">📋 Ringkasan Akhir — Top 5 Pekerjaan Paling Cocok</p>', unsafe_allow_html=True)
    summary_df = top1_avg.head(5)[['role_category', 'avg_match_pct', 'median_match_top1', 'user_count_top1']].copy()
    summary_df['median_pct'] = (summary_df['median_match_top1'] * 100).round(2)
    summary_df['rank'] = range(1, len(summary_df) + 1)
    st.dataframe(
        summary_df[['rank', 'role_category', 'avg_match_pct', 'median_pct', 'user_count_top1']]
        .rename(columns={
            'rank': 'Rank', 'role_category': 'Role Category',
            'avg_match_pct': 'Avg Match (%)', 'median_pct': 'Median Match (%)',
            'user_count_top1': 'Users Pilih sebagai #1'
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("""
    <div style="background: #1a1a2e; border: 1px solid #444466; border-radius: 10px; padding: 16px; margin-top: 16px;">
        <p style="color: #a78bfa; font-weight: 700; margin: 0 0 8px 0;">ℹ️ Metodologi</p>
        <p style="color: #aaaacc; margin: 0; font-size: 0.9rem;">
            <b>Match Score</b> = |Skills User ∩ Skill Pool Role| / |Skill Pool Role| × 100% &nbsp;|&nbsp;
            <b>Skill Gap</b> = Skills di pool role target yang tidak dimiliki user &nbsp;|&nbsp;
            <b>Crucial Score</b> = 0.5 × (% user gap) + 0.5 × (normalized job freq)
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color: #444466; font-size:0.8rem;">'
    'SkillScout Nusantara Dashboard · Dibuat dengan Streamlit</p>',
    unsafe_allow_html=True
)
