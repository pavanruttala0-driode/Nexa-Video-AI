import streamlit as st
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nexa Video AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        opacity: 0.75;
        margin-bottom: 30px;
    }

    .feature-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 15px;
    }

    .premium-card {
        padding: 25px;
        border-radius: 18px;
        border: 2px solid rgba(255, 180, 0, 0.5);
        text-align: center;
        margin-top: 20px;
    }

    .center {
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎬 Nexa Video AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Turn your words into amazing AI-powered videos</div>',
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# VIDEO INPUT
# =========================================================

st.subheader("✍️ Create Your Video")

text = st.text_area(
    "Enter your video idea or script",
    height=180,
    placeholder=(
        "Example:\n"
        "Create a motivational story about a student "
        "who works hard and becomes successful."
    )
)

# =========================================================
# VIDEO SETTINGS
# =========================================================

col1, col2 = st.columns(2)

with col1:

    language = st.selectbox(
        "🌐 Select Language",
        [
            "English",
            "Telugu",
            "Hindi",
            "Tamil",
            "Malayalam",
            "Kannada",
            "Bengali",
            "Marathi",
            "Gujarati",
            "Punjabi",
            "Urdu"
        ]
    )

with col2:

    duration = st.selectbox(
        "⏱️ Video Duration",
        [
            "5 minutes",
            "6 minutes",
            "8 minutes",
            "10 minutes"
        ]
    )

col3, col4 = st.columns(2)

with col3:

    voice = st.selectbox(
        "🎙️ Voice",
        [
            "Male",
            "Female"
        ]
    )

with col4:

    aspect_ratio = st.selectbox(
        "📱 Video Format",
        [
            "9:16 Portrait",
            "16:9 Landscape",
            "1:1 Square"
        ]
    )

# =========================================================
# VIDEO STYLE
# =========================================================

style = st.selectbox(
    "🎨 Video Style",
    [
        "Cinematic",
        "Realistic",
        "Cartoon",
        "Anime",
        "Educational",
        "Documentary",
        "Motivational",
        "Storytelling"
    ]
)

# =========================================================
# MUSIC
# =========================================================

music = st.selectbox(
    "🎵 Background Music",
    [
        "None",
        "Cinematic",
        "Motivational",
        "Emotional",
        "Upbeat",
        "Calm"
    ]
)

st.divider()

# =========================================================
# GENERATE VIDEO
# =========================================================

if st.button(
    "🚀 Generate Video",
    use_container_width=True,
    type="primary"
):

    if not text.strip():

        st.warning(
            "⚠️ Please enter your video idea or script first."
        )

    else:

        st.success(
            "✅ Video generation request created!"
        )

        st.session_state["video_requested"] = True
        st.session_state["video_text"] = text
        st.session_state["video_language"] = language
        st.session_state["video_duration"] = duration

# =========================================================
# VIDEO GENERATION STATUS
# =========================================================

if st.session_state.get("video_requested", False):

    st.divider()

    st.subheader("🎬 Video Generation")

    progress = st.progress(0)

    status = st.empty()

    status.info("Preparing your video...")

    progress.progress(15)

    status.info("🧠 Preparing AI script and scenes...")

    progress.progress(30)

    status.info("🎨 Preparing visual scenes...")

    progress.progress(45)

    status.info("🎙️ Preparing voice narration...")

    progress.progress(60)

    status.info("🎵 Preparing background music...")

    progress.progress(75)

    status.info(
        "🎬 Final video will be assembled here..."
    )

    progress.progress(100)

    st.success(
        "Video pipeline ready. Real AI generation will be connected next."
    )

    # =====================================================
    # VIDEO PREVIEW PLACEHOLDER
    # =====================================================

    st.subheader("▶️ Video Preview")

    st.info(
        "Your generated MP4 video will appear here after "
        "we connect the AI video-generation backend."
    )

    # =====================================================
    # DOWNLOAD PLACEHOLDER
    # =====================================================

    st.subheader("⬇️ Download")

    st.download_button(
        label="⬇️ Download Video",
        data=b"Nexa Video AI - Video will be generated here.",
        file_name="nexa_video.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.caption(
        "The download button is currently a prototype. "
        "It will download the actual MP4 after the video backend is connected."
    )

# =========================================================
# PREMIUM PLAN
# =========================================================

st.divider()

st.subheader("💎 Nexa Premium")

st.markdown(
    """
    <div class="premium-card">

    <h2>💎 Premium</h2>

    <h1>₹10 / month</h1>

    <p>✔ 5+ minute videos</p>
    <p>✔ Multiple languages</p>
    <p>✔ AI voice narration</p>
    <p>✔ AI visuals</p>
    <p>✔ Automatic subtitles</p>
    <p>✔ Video download</p>

    </div>
    """,
    unsafe_allow_html=True
)

st.button(
    "💳 Upgrade to Premium",
    use_container_width=True
)

# =========================================================
# FEATURES
# =========================================================

st.divider()

st.subheader("✨ Features")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown(
        """
        <div class="feature-card">
        <h3>🌐 Multiple Languages</h3>
        Create videos in different languages.
        </div>
        """,
        unsafe_allow_html=True
    )

with f2:
    st.markdown(
        """
        <div class="feature-card">
        <h3>🎬 Long Videos</h3>
        Create videos starting from 5 minutes.
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:
    st.markdown(
        """
        <div class="feature-card">
        <h3>⬇️ Download</h3>
        Download your generated MP4 videos.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    '<div class="center">🎬 Nexa Video AI • Turn Words Into Videos</div>',
    unsafe_allow_html=True
)
