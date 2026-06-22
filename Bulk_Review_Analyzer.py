import streamlit as st
import pickle
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ssl
# Fix SSL certificate issue on Windows
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
st.set_page_config(page_title="IMDB Review Analyzer", page_icon="⭐", layout="wide")
# LAZY LOAD NLTK
stop_words = None
def get_stopwords():
    global stop_words
    if stop_words is None:
        import nltk
        from nltk.corpus import stopwords
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        stop_words = set(stopwords.words('english'))
    return stop_words
# ===================== CINEMATIC CSS =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Montserrat:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #0F0F1A !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
}
/* hide default streamlit chrome */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
.stDeployButton { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
    padding-top: 0 !important;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
/* ── BACKGROUND PARTICLES ── */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(245,175,25,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(241,39,17,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(255,179,71,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
/* ── FLOATING ICONS ANIMATION ── */
@keyframes floatUp {
    0%   { transform: translateY(100vh) rotate(0deg);   opacity: 0; }
    10%  { opacity: 0.6; }
    90%  { opacity: 0.3; }
    100% { transform: translateY(-10vh) rotate(720deg); opacity: 0; }
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(245,175,25,0.4); }
    50%       { box-shadow: 0 0 40px rgba(245,175,25,0.8), 0 0 60px rgba(245,175,25,0.3); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes starPop {
    0%   { transform: scale(1); }
    50%  { transform: scale(1.3); }
    100% { transform: scale(1); }
}
@keyframes spotlightSweep {
    0%, 100% { opacity: 0.4; transform: rotate(-5deg); }
    50%       { opacity: 0.7; transform: rotate(5deg); }
}
@keyframes tickerMove {
    from { transform: translateX(100%); }
    to   { transform: translateX(-100%); }
}
/* ── FLOATING ICONS ── */
.floating-icons {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
}
.float-icon {
    position: absolute;
    font-size: 1.6rem;
    animation: floatUp linear infinite;
    bottom: -10%;
    opacity: 0;
}
.float-icon:nth-child(1)  { left: 5%;  animation-duration: 12s; animation-delay: 0s;   font-size: 1.2rem; }
.float-icon:nth-child(2)  { left: 15%; animation-duration: 15s; animation-delay: 2s;   font-size: 1.8rem; }
.float-icon:nth-child(3)  { left: 25%; animation-duration: 10s; animation-delay: 4s;   font-size: 1.4rem; }
.float-icon:nth-child(4)  { left: 38%; animation-duration: 18s; animation-delay: 1s;   font-size: 2.0rem; }
.float-icon:nth-child(5)  { left: 50%; animation-duration: 13s; animation-delay: 6s;   font-size: 1.3rem; }
.float-icon:nth-child(6)  { left: 62%; animation-duration: 16s; animation-delay: 3s;   font-size: 1.7rem; }
.float-icon:nth-child(7)  { left: 73%; animation-duration: 11s; animation-delay: 5s;   font-size: 1.5rem; }
.float-icon:nth-child(8)  { left: 85%; animation-duration: 14s; animation-delay: 7s;   font-size: 1.9rem; }
.float-icon:nth-child(9)  { left: 92%; animation-duration: 17s; animation-delay: 2.5s; font-size: 1.2rem; }
.float-icon:nth-child(10) { left: 45%; animation-duration: 20s; animation-delay: 8s;   font-size: 1.6rem; }
/* ── NAV BAR ── */
.cinematic-nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    width: 100%;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(15, 15, 26, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(245,175,25,0.15);
    animation: fadeInDown 0.6s ease;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Poppins', sans-serif;
    font-weight: 900;
    font-size: 1.3rem;
    background: linear-gradient(90deg, #F5AF19, #F12711, #FFB347);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}
.nav-logo-icon { font-size: 1.8rem; filter: drop-shadow(0 0 8px #F5AF19); }
.nav-links {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(245,175,25,0.2);
    border-radius: 50px;
    padding: 6px 10px;
}
.nav-link {
    padding: 8px 20px;
    border-radius: 50px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: #B8BCC8;
    transition: all 0.3s ease;
    white-space: nowrap;
    text-decoration: none;
}
.nav-link:hover { color: #F5AF19; background: rgba(245,175,25,0.1); }
.nav-link.active {
    background: linear-gradient(135deg, #F5AF19, #F12711);
    color: #fff !important;
    box-shadow: 0 4px 15px rgba(245,175,25,0.4);
}
.nav-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-clear-btn {
    padding: 8px 18px;
    border-radius: 50px;
    border: 1px solid rgba(241,39,17,0.4);
    background: transparent;
    color: #F12711;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}
.nav-clear-btn:hover { background: rgba(241,39,17,0.1); }
/* ── HERO SECTION ── */
.hero-section {
    position: relative;
    width: 100%;
    min-height: 440px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 70px 20px 80px;
    overflow: hidden;
    background:
        radial-gradient(ellipse 70% 80% at 50% 50%, rgba(241,39,17,0.12) 0%, transparent 70%),
        linear-gradient(180deg, #0F0F1A 0%, #1A0A00 50%, #0F0F1A 100%);
    animation: fadeInUp 0.8s ease;
}
/* spotlight cones */
.hero-section::before, .hero-section::after {
    content: '';
    position: absolute;
    top: -60px;
    width: 300px;
    height: 600px;
    background: linear-gradient(180deg, rgba(245,175,25,0.18) 0%, transparent 80%);
    border-radius: 50%;
    animation: spotlightSweep 6s ease-in-out infinite;
}
.hero-section::before { left: -60px;  transform-origin: top left; }
.hero-section::after  { right: -60px; transform-origin: top right; animation-delay: 3s; }
/* film strip edges */
.film-strip-left, .film-strip-right {
    position: absolute;
    top: 0; bottom: 0;
    width: 32px;
    background: repeating-linear-gradient(
        180deg,
        #1a1a2e 0px, #1a1a2e 14px,
        #2a2a3e 14px, #2a2a3e 22px
    );
    opacity: 0.5;
    border-radius: 4px;
}
.film-strip-left  { left: 0; }
.film-strip-right { right: 0; }
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,175,25,0.15);
    border: 1px solid rgba(245,175,25,0.4);
    border-radius: 50px;
    padding: 6px 18px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #F5AF19;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 900;
    font-size: clamp(2.4rem, 6vw, 4.2rem);
    line-height: 1.1;
    background: linear-gradient(135deg, #FFFFFF 20%, #F5AF19 50%, #FFB347 70%, #F12711 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
    margin-bottom: 14px;
    text-shadow: none;
    position: relative; z-index: 1;
}
.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: clamp(0.95rem, 2vw, 1.15rem);
    color: #B8BCC8;
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 32px;
    position: relative; z-index: 1;
}
.hero-cta {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #F5AF19, #F12711);
    color: #fff;
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    padding: 14px 36px;
    border-radius: 50px;
    border: none;
    cursor: pointer;
    animation: pulse 2.5s ease-in-out infinite;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative; z-index: 1;
    text-decoration: none;
}
.hero-cta:hover { transform: scale(1.05); }
/* ── PAGE WRAPPER ── */
.page-wrapper {
    position: relative;
    z-index: 1;
    padding: 32px 40px 60px;
    max-width: 1280px;
    margin: 0 auto;
    animation: fadeInUp 0.6s ease 0.1s both;
}
/* ── SECTION TITLE ── */
.section-title {
    font-family: 'Montserrat', sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: #FFFFFF;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(245,175,25,0.4), transparent);
    margin-left: 10px;
}
/* ── GLASS CARD ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px;
    backdrop-filter: blur(12px);
    transition: transform 0.3s, box-shadow 0.3s;
}
.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(245,175,25,0.1);
}
/* ── METRIC TICKET CARDS ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.metric-ticket {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(245,175,25,0.2);
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
}
.metric-ticket::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(245,175,25,0.06), transparent);
    pointer-events: none;
}
.metric-ticket:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(245,175,25,0.15);
    border-color: rgba(245,175,25,0.5);
}
.metric-icon { font-size: 1.8rem; margin-bottom: 6px; }
.metric-value {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 1.9rem;
    background: linear-gradient(135deg, #F5AF19, #FFB347);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    font-size: 0.75rem;
    color: #B8BCC8;
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
/* ── RATING DISPLAY ── */
.rating-showcase {
    background: rgba(245,175,25,0.07);
    border: 1px solid rgba(245,175,25,0.25);
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    margin-bottom: 20px;
}
.rating-big {
    font-family: 'Poppins', sans-serif;
    font-weight: 900;
    font-size: 3.5rem;
    background: linear-gradient(135deg, #F5AF19, #FFB347);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.rating-stars-display { font-size: 1.8rem; margin: 8px 0; letter-spacing: 4px; }
.rating-sub { color: #B8BCC8; font-size: 0.9rem; }
/* ── REVIEW CARD ── */
.review-card-cinema {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 4px solid;
    border-image: linear-gradient(180deg, #F5AF19, #F12711) 1;
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 14px;
    transition: transform 0.25s, box-shadow 0.25s;
    position: relative;
    overflow: hidden;
}
.review-card-cinema:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(245,175,25,0.12);
}
.review-card-cinema::before {
    content: '"';
    position: absolute;
    top: -10px; right: 16px;
    font-size: 5rem;
    color: rgba(245,175,25,0.08);
    font-family: Georgia, serif;
    line-height: 1;
}
.review-stars-row { font-size: 1.2rem; margin-bottom: 6px; color: #F5AF19; }
.review-quote {
    font-style: italic;
    color: #FFFFFF;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 10px;
    padding: 10px 14px;
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}
.review-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}
.review-timestamp { color: #B8BCC8; font-size: 0.8rem; }
.review-rating-badge {
    background: linear-gradient(135deg, #F5AF19, #F12711);
    color: #fff;
    font-weight: 700;
    font-size: 0.78rem;
    padding: 3px 12px;
    border-radius: 50px;
}
/* ── HISTORY REVIEW CARD ── */
.hist-review-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 14px;
    transition: transform 0.25s, box-shadow 0.25s;
    position: relative;
}
.hist-review-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(245,175,25,0.1);
    border-color: rgba(245,175,25,0.2);
}
.hist-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    flex-wrap: wrap;
    gap: 8px;
}
.hist-review-num {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 0.82rem;
    color: #B8BCC8;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.hist-stars { font-size: 1.1rem; color: #F5AF19; }
.hist-rating-pill {
    background: linear-gradient(135deg, rgba(245,175,25,0.2), rgba(241,39,17,0.2));
    border: 1px solid rgba(245,175,25,0.3);
    border-radius: 50px;
    padding: 3px 14px;
    font-weight: 700;
    font-size: 0.82rem;
    color: #F5AF19;
}
.hist-review-text {
    color: #FFFFFF;
    font-size: 0.93rem;
    line-height: 1.6;
    margin: 10px 0;
    padding: 12px 14px;
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.05);
    font-style: italic;
}
.hist-timestamp { color: #B8BCC8; font-size: 0.8rem; margin-top: 6px; }
/* ── COMMENT BOX ── */
.comment-cinema {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid rgba(245,175,25,0.5);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    color: #FFFFFF;
    font-size: 0.88rem;
}
.comment-time { color: #B8BCC8; font-size: 0.75rem; margin-top: 4px; }
/* ── INSIGHTS ── */
.insights-model-card {
    background: rgba(245,175,25,0.06);
    border: 1px solid rgba(245,175,25,0.2);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.insights-model-card h3 {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    color: #F5AF19;
    margin-bottom: 6px;
}
.insights-model-card p { color: #B8BCC8; font-size: 0.88rem; }
.insights-acc-card {
    background: rgba(46,204,113,0.08);
    border: 1px solid rgba(46,204,113,0.25);
    border-radius: 16px;
    padding: 24px;
}
.insights-acc-card h3 {
    font-family: 'Poppins', sans-serif;
    font-weight: 900;
    font-size: 2.4rem;
    color: #2ECC71;
    margin-bottom: 4px;
}
.insights-acc-card p { color: #B8BCC8; font-size: 0.88rem; }
/* ── STAT METRIC (insights page) ── */
.stat-metric {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: transform 0.2s;
}
.stat-metric:hover { transform: translateX(4px); border-color: rgba(245,175,25,0.25); }
.stat-metric-icon { font-size: 1.6rem; }
.stat-metric-content {}
.stat-metric-value {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: #F5AF19;
}
.stat-metric-label { color: #B8BCC8; font-size: 0.8rem; }
/* ── FILTER BAR ── */
.filter-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px 20px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
}
/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #B8BCC8;
}
.empty-state .empty-icon { font-size: 4rem; margin-bottom: 16px; }
.empty-state h3 { color: #FFFFFF; font-family: 'Montserrat', sans-serif; font-weight: 700; margin-bottom: 8px; }
/* ── STREAMLIT OVERRIDES ── */
/* label text */
[data-testid="stWidgetLabel"] p,
.stSlider label,
.stTextArea label,
.stSelectbox label { color: #B8BCC8 !important; font-family: 'Inter', sans-serif !important; }
/* select slider */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: linear-gradient(135deg, #F5AF19, #F12711) !important;
    border: none !important;
    box-shadow: 0 0 12px rgba(245,175,25,0.6) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[class*="thumb"] {
    background: linear-gradient(135deg, #F5AF19, #F12711) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[class*="track"] div:first-child {
    background: linear-gradient(90deg, #F5AF19, #F12711) !important;
}
/* textarea */
.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(245,175,25,0.25) !important;
    border-radius: 14px !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 14px !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(245,175,25,0.7) !important;
    box-shadow: 0 0 20px rgba(245,175,25,0.2) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #666 !important; }
/* selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}
/* primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #F5AF19, #F12711) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 12px 28px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(245,175,25,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 6px 28px rgba(245,175,25,0.5) !important;
}
/* secondary button */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    color: #B8BCC8 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 50px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(245,175,25,0.4) !important;
    color: #F5AF19 !important;
    background: rgba(245,175,25,0.08) !important;
}
/* generic stButton */
.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 50px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: rgba(245,175,25,0.35) !important;
    background: rgba(245,175,25,0.08) !important;
}
/* info box */
.stInfo {
    background: rgba(245,175,25,0.08) !important;
    border: 1px solid rgba(245,175,25,0.25) !important;
    border-radius: 12px !important;
    color: #F5AF19 !important;
}
/* success box */
.stSuccess {
    background: rgba(46,204,113,0.1) !important;
    border: 1px solid rgba(46,204,113,0.3) !important;
    border-radius: 12px !important;
    color: #2ECC71 !important;
}
/* expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: #B8BCC8 !important; }
/* divider */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 20px 0 !important; }
/* caption */
.stCaption, [data-testid="stCaptionContainer"] p { color: #B8BCC8 !important; }
/* plotly dark bg */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
/* required star */
.required { color: #F12711 !important; font-weight: 700 !important; }
/* ticker bar */
.ticker-bar {
    width: 100%;
    background: rgba(245,175,25,0.08);
    border-top: 1px solid rgba(245,175,25,0.15);
    border-bottom: 1px solid rgba(245,175,25,0.15);
    padding: 8px 0;
    overflow: hidden;
    white-space: nowrap;
    margin-bottom: 0;
}
.ticker-content {
    display: inline-block;
    animation: tickerMove 30s linear infinite;
    font-size: 0.8rem;
    color: #B8BCC8;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.ticker-content span { margin: 0 28px; }
.ticker-content .hi { color: #F5AF19; }
/* responsive */
@media (max-width: 768px) {
    .metrics-row { grid-template-columns: repeat(2, 1fr); }
    .cinematic-nav { padding: 12px 16px; }
    .nav-logo span { display: none; }
    .page-wrapper { padding: 20px 16px 40px; }
}
</style>
""", unsafe_allow_html=True)
# ── Floating icons ──
st.markdown("""
<div class="floating-icons">
  <div class="float-icon">🎬</div>
  <div class="float-icon">⭐</div>
  <div class="float-icon">🍿</div>
  <div class="float-icon">🎭</div>
  <div class="float-icon">🎥</div>
  <div class="float-icon">🎞️</div>
  <div class="float-icon">🏆</div>
  <div class="float-icon">🎫</div>
  <div class="float-icon">🌟</div>
  <div class="float-icon">🎬</div>
</div>
""", unsafe_allow_html=True)
@st.cache_resource
def load_model():
    model = pickle.load(open("models/sentiment_model.pkl", "rb"))
    tfidf = pickle.load(open("models/tfidf.pkl", "rb"))
    return model, tfidf
model, tfidf = load_model()
def clean_text(text):
    sw = get_stopwords()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    words = text.split()
    words = [w for w in words if w not in sw]
    return ' '.join(words)
def predict_sentiment(review):
    cleaned = clean_text(review)
    if len(cleaned.split()) == 0:
        return None, 0, 0
    vector = tfidf.transform([cleaned])
    prediction = model.predict(vector)[0]
    proba = model.predict_proba(vector)[0]
    return prediction, proba[0], proba[1]
def stars_to_rating(stars):
    return stars * 2
# ── Session state ──
if 'all_reviews' not in st.session_state:
    st.session_state.all_reviews = []
if 'page' not in st.session_state:
    st.session_state.page = 'Review'
# ── Handle nav from URL params ──
qp = st.query_params
if 'nav' in qp:
    st.session_state.page = qp['nav']
# ── TOP NAVIGATION BAR ──
current = st.session_state.page
nav_html = f"""
<nav class="cinematic-nav">
  <div class="nav-logo">
    <span class="nav-logo-icon">🎬</span>
    <span>CineReview</span>
  </div>
  <div class="nav-links">
    <span class="nav-link {'active' if current=='Review' else ''}"
          onclick="window.location.href='?nav=Review'" style="cursor:pointer;">⭐ Review</span>
    <span class="nav-link {'active' if current=='History' else ''}"
          onclick="window.location.href='?nav=History'" style="cursor:pointer;">📜 History</span>
    <span class="nav-link {'active' if current=='Insights' else ''}"
          onclick="window.location.href='?nav=Insights'" style="cursor:pointer;">📊 Insights</span>
  </div>
  <div class="nav-actions">
    <!-- clear handled by st.button below -->
  </div>
</nav>
"""
st.markdown(nav_html, unsafe_allow_html=True)
# Streamlit nav buttons (invisible triggers)
nav_col1, nav_col2, nav_col3, nav_col4, _ = st.columns([1,1,1,1,6])
with nav_col1:
    if st.button("⭐ Review", key="nav_review"):
        st.session_state.page = 'Review'
        st.rerun()
with nav_col2:
    if st.button("📜 History", key="nav_history"):
        st.session_state.page = 'History'
        st.rerun()
with nav_col3:
    if st.button("📊 Insights", key="nav_insights"):
        st.session_state.page = 'Insights'
        st.rerun()
with nav_col4:
    if st.button("🗑️ Clear", key="nav_clear"):
        st.session_state.all_reviews = []
        st.rerun()
# ── TICKER ──
st.markdown("""
<div class="ticker-bar">
  <div class="ticker-content">
    <span>🎬 <span class="hi">NOW ANALYZING</span> · Your reviews power our AI</span>
    <span>⭐ <span class="hi">POWERED BY ML</span> · Logistic Regression + TF-IDF</span>
    <span>🍿 Rate movies · Share thoughts · Discover sentiment</span>
    <span>🏆 <span class="hi">89% ACCURACY</span> · Trained on 50,000 IMDB reviews</span>
    <span>🎭 Premium Cinema Analytics · Your personal box office</span>
    <span>🌟 <span class="hi">CINEREVIEW</span> · Where every opinion counts</span>
  </div>
</div>
""", unsafe_allow_html=True)
# ════════════════════════════════════════════════════
#  PAGE 1 — REVIEW
# ════════════════════════════════════════════════════
if st.session_state.page == 'Review':
    # Hero
    st.markdown("""
    <div class="hero-section">
      <div class="film-strip-left"></div>
      <div class="film-strip-right"></div>
      <div class="hero-badge">🎬 Premium Cinema Analytics</div>
      <h1 class="hero-title">⭐ IMDB REVIEW ANALYZER</h1>
      <p class="hero-subtitle">Share Your Movie Experience &amp; Discover Audience Sentiment powered by Machine Learning</p>
      <div class="hero-cta">🎬 Submit Your Review Below</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-wrapper">', unsafe_allow_html=True)
    # Metrics row (top)
    if st.session_state.all_reviews:
        df_m = pd.DataFrame(st.session_state.all_reviews)
        avg_r = df_m['rating'].mean()
        avg_s = df_m['stars'].mean()
        tot_pos = (df_m['sentiment'] == 'Positive').sum()
        aud_score = int(tot_pos / len(df_m) * 100)
        st.markdown(f"""
        <div class="metrics-row">
          <div class="metric-ticket">
            <div class="metric-icon">🎫</div>
            <div class="metric-value">{len(df_m)}</div>
            <div class="metric-label">Total Reviews</div>
          </div>
          <div class="metric-ticket">
            <div class="metric-icon">⭐</div>
            <div class="metric-value">{avg_r:.1f}</div>
            <div class="metric-label">Avg Rating /10</div>
          </div>
          <div class="metric-ticket">
            <div class="metric-icon">👍</div>
            <div class="metric-value">{tot_pos}</div>
            <div class="metric-label">Positive Reviews</div>
          </div>
          <div class="metric-ticket">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">{aud_score}%</div>
            <div class="metric-label">Audience Score</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown('<div class="section-title">🎬 Submit Your Review</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("**⭐ Star Rating** <span class='required'>*</span>", unsafe_allow_html=True)
            star_rating = st.select_slider("Select your rating:", options=[1,2,3,4,5], value=5, label_visibility="collapsed")
            stars_display = '⭐' * star_rating + '☆' * (5 - star_rating)
            st.markdown(f"""
            <div style="text-align:center; font-size:2.2rem; letter-spacing:6px; margin:10px 0 4px;">
              {stars_display}
            </div>
            <div style="text-align:center; color:#B8BCC8; font-size:0.85rem; margin-bottom:16px;">
              {star_rating}/5 stars &nbsp;·&nbsp; {stars_to_rating(star_rating)}/10 IMDB score
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**📝 Written Review** *(Optional)*")
            user_text = st.text_area(
                "Written Review",
                height=130,
                placeholder='"The cinematography was breathtaking — every frame felt like a painting…"',
                label_visibility="collapsed"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Submit Review", type="primary", use_container_width=True):
                rating = stars_to_rating(star_rating)
                has_text = user_text.strip() != ""
                if has_text:
                    pred, neg_p, pos_p = predict_sentiment(user_text)
                    sentiment = 'Positive' if pred == 1 else 'Negative' if pred is not None else 'Neutral'
                else:
                    sentiment = 'Positive' if star_rating >= 3 else 'Negative'
                st.session_state.all_reviews.append({
                    'id': len(st.session_state.all_reviews),
                    'review': str(user_text).strip(),
                    'sentiment': sentiment,
                    'rating': rating,
                    'stars': star_rating,
                    'review_method': 'Stars + Text' if has_text else 'Stars Only',
                    'likes': 0,
                    'comments': [],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                if has_text:
                    st.success(f"🎬 Review submitted! ⭐ {rating}/10 — Sentiment: {sentiment}")
                else:
                    st.success(f"🎬 Rating submitted! ⭐ {rating}/10 — Sentiment: {sentiment}")
                st.rerun()
    with col2:
        st.markdown('<div class="section-title">📊 Audience Rating</div>', unsafe_allow_html=True)
        if not st.session_state.all_reviews:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">🎭</div>
              <h3>No Reviews Yet</h3>
              <p>Submit your first review to see the audience rating</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            df2 = pd.DataFrame(st.session_state.all_reviews)
            avg_rating2 = df2['rating'].mean()
            avg_stars2 = df2['stars'].mean()
            filled = '⭐' * round(avg_stars2)
            st.markdown(f"""
            <div class="rating-showcase">
              <div class="rating-big">{avg_rating2:.1f}<span style="font-size:1.4rem;color:#B8BCC8;">/10</span></div>
              <div class="rating-stars-display">{filled}</div>
              <div class="rating-sub">{avg_stars2:.1f}/5 average · Based on {len(df2)} review{'s' if len(df2)!=1 else ''}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="margin-top:24px;">🎥 Recent Reviews</div>', unsafe_allow_html=True)
            for rev in reversed(st.session_state.all_reviews[-5:]):
                review_text = str(rev.get('review', '')).strip()
                stars_html = '⭐' * rev['stars'] + '<span style="opacity:.3">☆</span>' * (5 - rev['stars'])
                quote_block = f'<div class="review-quote">📝 {review_text}</div>' if review_text else ''
                st.markdown(f"""
                <div class="review-card-cinema">
                  <div class="review-stars-row">{stars_html}</div>
                  {quote_block}
                  <div class="review-meta">
                    <span class="review-timestamp">🕒 {rev['timestamp']}</span>
                    <span class="review-rating-badge">{rev['rating']}/10</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
# ════════════════════════════════════════════════════
#  PAGE 2 — HISTORY
# ════════════════════════════════════════════════════
elif st.session_state.page == 'History':
    st.markdown("""
    <div class="hero-section" style="min-height:220px; padding:48px 20px;">
      <div class="film-strip-left"></div>
      <div class="film-strip-right"></div>
      <div class="hero-badge">📜 Review Archive</div>
      <h1 class="hero-title" style="font-size:clamp(1.8rem,4vw,3rem);">All Reviews</h1>
      <p class="hero-subtitle" style="margin-bottom:0;">Your complete cinema review history</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-wrapper">', unsafe_allow_html=True)
    if not st.session_state.all_reviews:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>No Reviews Yet</h3>
          <p>Head to the Review page to add your first movie review</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Go to Review Page", type="primary"):
            st.session_state.page = 'Review'
            st.rerun()
    else:
        # Filter bar
        f1, f2, f3 = st.columns([2, 2, 1])
        with f1:
            filter_method = st.selectbox("Filter by Type", ["All", "Stars Only", "Stars + Text"])
        with f2:
            sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Rating", "Most Liked"])
        with f3:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        reviews_to_show = st.session_state.all_reviews.copy()
        if filter_method != "All":
            reviews_to_show = [r for r in reviews_to_show if r['review_method'] == filter_method]
        if sort_by == "Newest First":
            reviews_to_show = list(reversed(reviews_to_show))
        elif sort_by == "Oldest First":
            pass
        elif sort_by == "Highest Rating":
            reviews_to_show = sorted(reviews_to_show, key=lambda x: x['rating'], reverse=True)
        elif sort_by == "Most Liked":
            reviews_to_show = sorted(reviews_to_show, key=lambda x: x['likes'], reverse=True)
        st.markdown(f"""
        <div style="color:#B8BCC8; font-size:0.88rem; margin-bottom:20px;">
          Showing <span style="color:#F5AF19; font-weight:700;">{len(reviews_to_show)}</span> of
          <span style="color:#FFFFFF; font-weight:700;">{len(st.session_state.all_reviews)}</span> reviews
        </div>
        """, unsafe_allow_html=True)
        for rev in reviews_to_show:
            real_idx = rev['id']
            review_text = str(rev.get('review', '')).strip()
            safe_text = review_text if review_text and '<small>' not in review_text else ''
            text_block = f'<div class="hist-review-text">📝 {safe_text}</div>' if safe_text else ''
            stars_html = '⭐' * rev['stars']
            st.markdown(f"""
            <div class="hist-review-card">
              <div class="hist-card-header">
                <span class="hist-review-num">Review #{rev['id']+1}</span>
                <span class="hist-stars">{stars_html}</span>
                <span class="hist-rating-pill">⭐ {rev['rating']}/10</span>
              </div>
              {text_block}
              <div class="hist-timestamp">🕒 {rev['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
            lc1, lc2, _ = st.columns([1, 1, 6])
            with lc1:
                if st.button(f"👍 {rev['likes']}", key=f"like_{real_idx}"):
                    st.session_state.all_reviews[real_idx]['likes'] += 1
                    st.rerun()
            with lc2:
                st.write(f"💬 {len(rev['comments'])}")
            with st.expander(f"💬 Comments ({len(rev['comments'])})", expanded=False):
                if rev['comments']:
                    for comment in rev['comments']:
                        st.markdown(f"""
                        <div class="comment-cinema">
                          💬 {comment['text']}
                          <div class="comment-time">🕒 {comment['time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No comments yet. Be the first!")
                st.markdown("---")
                new_comment = st.text_input("Write a comment", key=f"comment_input_{real_idx}",
                                            placeholder="Share your thoughts…")
                cp1, _ = st.columns([1, 5])
                with cp1:
                    if st.button("Post", key=f"post_{real_idx}", type="primary"):
                        if new_comment.strip():
                            st.session_state.all_reviews[real_idx]['comments'].append({
                                'text': new_comment,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            st.rerun()
                        else:
                            st.warning("Comment cannot be empty")
    st.markdown('</div>', unsafe_allow_html=True)
# ════════════════════════════════════════════════════
#  PAGE 3 — INSIGHTS
# ════════════════════════════════════════════════════
elif st.session_state.page == 'Insights':
    st.markdown("""
    <div class="hero-section" style="min-height:220px; padding:48px 20px;">
      <div class="film-strip-left"></div>
      <div class="film-strip-right"></div>
      <div class="hero-badge">📊 Cinema Analytics</div>
      <h1 class="hero-title" style="font-size:clamp(1.8rem,4vw,3rem);">Model Insights & Analytics</h1>
      <p class="hero-subtitle" style="margin-bottom:0;">Professional performance metrics &amp; review analytics</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-wrapper">', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-title">🤖 Model Performance</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insights-model-card">
          <h3>Logistic Regression</h3>
          <p>Algorithm: Scikit-learn &nbsp;|&nbsp; Vectorizer: TF-IDF (5,000 features)</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="margin-top:20px;">📈 Accuracy Score</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insights-acc-card">
          <h3>89.0%</h3>
          <p>Model accuracy on IMDB test dataset (50,000 reviews)</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-title">📊 Your Session Stats</div>', unsafe_allow_html=True)
        if not st.session_state.all_reviews:
            st.markdown("""
            <div class="empty-state" style="padding:40px 20px;">
              <div class="empty-icon">📭</div>
              <h3>No Data Yet</h3>
              <p>Add reviews on the Review page to see your analytics</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            df3 = pd.DataFrame(st.session_state.all_reviews)
            pos_rate = (df3['sentiment']=='Positive').sum() / len(df3) * 100
            st.markdown(f"""
            <div class="stat-metric">
              <span class="stat-metric-icon">🎫</span>
              <div class="stat-metric-content">
                <div class="stat-metric-value">{len(df3)}</div>
                <div class="stat-metric-label">Total Reviews Analyzed</div>
              </div>
            </div>
            <div class="stat-metric">
              <span class="stat-metric-icon">⭐</span>
              <div class="stat-metric-content">
                <div class="stat-metric-value">{df3['rating'].mean():.2f}/10</div>
                <div class="stat-metric-label">Average Rating</div>
              </div>
            </div>
            <div class="stat-metric">
              <span class="stat-metric-icon">🌟</span>
              <div class="stat-metric-content">
                <div class="stat-metric-value">{df3['stars'].mean():.2f} ⭐</div>
                <div class="stat-metric-label">Average Stars</div>
              </div>
            </div>
            <div class="stat-metric">
              <span class="stat-metric-icon">👍</span>
              <div class="stat-metric-content">
                <div class="stat-metric-value">{pos_rate:.0f}%</div>
                <div class="stat-metric-label">Positive Rate</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.all_reviews:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📊</div>
          <h3>Charts Will Appear Here</h3>
          <p>Add at least one review to see your analytics charts</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df4 = pd.DataFrame(st.session_state.all_reviews)
        PLOT_LAYOUT = dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.02)',
            font=dict(color='#B8BCC8', family='Inter'),
            title_font=dict(color='#FFFFFF', family='Montserrat', size=15),
            margin=dict(t=50, b=30, l=20, r=20),
            height=380,
        )
        # Row 1
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown('<div class="section-title">📊 Sentiment Distribution</div>', unsafe_allow_html=True)
            sc = df4['sentiment'].value_counts().reset_index()
            sc.columns = ['Sentiment', 'Count']
            fig_bar = px.bar(sc, x='Sentiment', y='Count', color='Sentiment',
                             color_discrete_map={'Positive':'#2ECC71','Negative':'#E74C3C','Neutral':'#95A5A6'})
            fig_bar.update_layout(**PLOT_LAYOUT, showlegend=False)
            fig_bar.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(fig_bar, use_container_width=True)
        with col4:
            st.markdown('<div class="section-title">⭐ Rating Distribution</div>', unsafe_allow_html=True)
            fig_hist = px.histogram(df4, x='rating', nbins=10,
                                    labels={'rating':'IMDB Rating','count':'Reviews'},
                                    color_discrete_sequence=['#F5AF19'])
            fig_hist.update_layout(**PLOT_LAYOUT)
            fig_hist.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(fig_hist, use_container_width=True)
        # Row 2
        col5, col6 = st.columns(2, gap="large")
        with col5:
            st.markdown('<div class="section-title">🎯 Average Rating Gauge</div>', unsafe_allow_html=True)
            avg_r2 = df4['rating'].mean()
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_r2,
                domain={'x':[0,1],'y':[0,1]},
                title={'text':'Overall Rating /10','font':{'size':15,'color':'#FFFFFF','family':'Montserrat'}},
                number={'font':{'color':'#F5AF19','size':48,'family':'Poppins'}},
                gauge={
                    'axis':{'range':[0,10],'tickcolor':'#B8BCC8','tickwidth':1},
                    'bar':{'color':'#F5AF19','thickness':0.25},
                    'bgcolor':'rgba(255,255,255,0.04)',
                    'borderwidth':0,
                    'steps':[
                        {'range':[0,4],'color':'rgba(231,76,60,0.25)'},
                        {'range':[4,7],'color':'rgba(243,156,18,0.25)'},
                        {'range':[7,10],'color':'rgba(46,204,113,0.25)'}
                    ],
                    'threshold':{'line':{'color':'#F12711','width':3},'thickness':0.75,'value':9}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=380,
                                    font=dict(color='#B8BCC8',family='Inter'))
            st.plotly_chart(fig_gauge, use_container_width=True)
        with col6:
            st.markdown('<div class="section-title">📋 Review Method Breakdown</div>', unsafe_allow_html=True)
            mc = df4['review_method'].value_counts().reset_index()
            mc.columns = ['Method','Count']
            fig_donut = px.pie(mc, values='Count', names='Method',
                               color_discrete_sequence=['#F5AF19','#F12711'], hole=0.45)
            fig_donut.update_traces(textposition='inside', textinfo='percent+label',
                                    textfont=dict(color='#FFFFFF', size=12),
                                    marker=dict(line=dict(color='rgba(0,0,0,0.3)', width=2)))
            fig_donut.update_layout(**PLOT_LAYOUT, showlegend=True,
                                    legend=dict(font=dict(color='#B8BCC8')))
            st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
# ── footer ──
st.markdown("""
<div style="text-align:center; padding:32px 20px; color:#B8BCC8; font-size:0.8rem;
            border-top:1px solid rgba(255,255,255,0.05); margin-top:40px;">
  <span style="color:#F5AF19; font-weight:700;">🎬 CineReview</span>
  &nbsp;·&nbsp; Built with Streamlit + Scikit-learn + TF-IDF
  &nbsp;·&nbsp; <span style="color:#F5AF19;">89%</span> Model Accuracy
</div>
""", unsafe_allow_html=True)