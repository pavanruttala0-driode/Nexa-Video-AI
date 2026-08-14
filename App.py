import streamlit as st

st.set_page_config(
    page_title="Nexa Video AI",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Nexa Video AI")
st.subheader("Turn your ideas into AI-powered videos")

st.divider()

text = st.text_area(
    "✍️ Enter your video idea or script",
    placeholder="Example: Create a motivational story about a student who becomes successful..."
)

col1, col2 = st.columns(2)

with col1:
    language = st.selectbox(
        "🌐 Language",
        [
            "English",
            "Telugu",
            "Hindi",
            "Tamil",
            "Malayalam",
            "Kannada",
            "Bengali",
            "Marathi"
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
        ["Male", "Female"]
    )

with col4:
    aspect_ratio = st.selectbox(
        "📱 Video Format",
        ["9:16 Portrait", "16:9 Landscape", "1:1 Square"]
    )

st.divider()

if st.button("🚀 Generate Video", use_container_width=True):

    if not text.strip():
        st.warning("Please enter your video idea or script first.")
    else:
        st.success("Your video request has been received!")

        st.write("### 🎬 Video Settings")
        st.write(f"**Language:** {language}")
        st.write(f"**Duration:** {duration}")
        st.write(f"**Voice:** {voice}")
        st.write(f"**Format:** {aspect_ratio}")

        st.info(
            "AI video generation will be connected in the next step."
        )

st.divider()

st.caption("Nexa Video AI • Turn Words Into Videos")
