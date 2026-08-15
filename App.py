import time
import os
import tempfile
import requests
import streamlit as st

from google import genai
from google.genai import types


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Nexa Video AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SECRETS
# =========================================================

FIREBASE_API_KEY = st.secrets.get(
    "FIREBASE_API_KEY",
    ""
)

GEMINI_API_KEY = st.secrets.get(
    "GEMINI_API_KEY",
    ""
)


# =========================================================
# SETTINGS
# =========================================================

GEMINI_MODEL = "gemini-3.6-flash"

VEO_MODEL = "veo-3.1-fast-generate-preview"

FIREBASE_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)

GEMINI_INTERACTION_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/interactions"
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "id_token" not in st.session_state:
    st.session_state.id_token = ""

if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""

if "video_path" not in st.session_state:
    st.session_state.video_path = ""

if "videos_today" not in st.session_state:
    st.session_state.videos_today = 0


# =========================================================
# SAFETY FILTER
# =========================================================

def is_unsafe_content(text):

    blocked_terms = [
        "porn",
        "pornography",
        "xxx",
        "nude",
        "nudity",
        "nsfw",
        "erotic",
        "sexual content",
        "sexual video",
        "sex video",
        "adult video",
        "adult content",
        "explicit sex",
        "sexually explicit",
        "sexual intercourse",
        "18+ video",
        "18 plus video",
        "onlyfans",

        "బూతు",
        "నగ్న",
        "అశ్లీల",
        "సెక్స్ వీడియో",

        "अश्लील",
        "नग्न",
        "सेक्स वीडियो",

        "ஆபாச",
        "நிர்வாண",
        "செக்ஸ் வீடியோ"
    ]

    text = text.lower()

    for term in blocked_terms:
        if term in text:
            return True

    return False


# =========================================================
# FIREBASE SIGNUP
# =========================================================

def firebase_signup(email, password):

    url = (
        f"{FIREBASE_URL}:signUp"
        f"?key={FIREBASE_API_KEY}"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        },
        timeout=30
    )

    return response.json()


# =========================================================
# FIREBASE LOGIN
# =========================================================

def firebase_login(email, password):

    url = (
        f"{FIREBASE_URL}:signInWithPassword"
        f"?key={FIREBASE_API_KEY}"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        },
        timeout=30
    )

    return response.json()


# =========================================================
# GEMINI SCRIPT GENERATION
# =========================================================

def generate_script(prompt):

    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is missing."

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": GEMINI_MODEL,
        "input": prompt
    }

    try:

        response = requests.post(
            GEMINI_INTERACTION_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        data = response.json()

        if response.status_code >= 400:

            return None, (
                f"Gemini API error "
                f"{response.status_code}: "
                f"{data}"
            )

        output_text = data.get(
            "output_text"
        )

        if output_text:
            return output_text, None

        collected = []

        for step in data.get("steps", []):

            if step.get("type") != "model_output":
                continue

            for content in step.get(
                "content",
                []
            ):

                if content.get("type") == "text":

                    text = content.get(
                        "text",
                        ""
                    )

                    if text:
                        collected.append(text)

        if collected:
            return "\n".join(collected), None

        return None, (
            "Gemini responded but no text "
            "was found."
        )

    except Exception as e:

        return None, str(e)


# =========================================================
# VEO VIDEO GENERATION
# =========================================================

def generate_veo_video(
    prompt,
    aspect_ratio="9:16"
):

    if not GEMINI_API_KEY:

        return None, (
            "GEMINI_API_KEY is missing."
        )

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        st.info(
            "🎬 Starting Veo video generation..."
        )

        operation = client.models.generate_videos(
            model=VEO_MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                resolution="720p",
                number_of_videos=1
            )
        )

        progress = st.progress(0)

        status = st.empty()

        start_time = time.time()

        while not operation.done:

            elapsed = int(
                time.time() - start_time
            )

            status.write(
                f"🎬 Generating video... "
                f"{elapsed}s elapsed"
            )

            progress.progress(
                min(
                    0.95,
                    0.05 + elapsed / 180
                )
            )

            time.sleep(10)

            operation = client.operations.get(
                operation
            )

        progress.progress(1.0)

        status.write(
            "✅ Video generation completed!"
        )

        if not operation.response:

            return None, (
                "Veo returned no response."
            )

        generated_videos = (
            operation.response.generated_videos
        )

        if not generated_videos:

            return None, (
                "Veo returned no generated video."
            )

        generated_video = (
            generated_videos[0]
        )

        client.files.download(
            file=generated_video.video
        )

        output_path = os.path.join(
            tempfile.gettempdir(),
            "nexa_video.mp4"
        )

        generated_video.video.save(
            output_path
        )

        if not os.path.exists(
            output_path
        ):

            return None, (
                "Video file was not saved."
            )

        return output_path, None

    except Exception as e:

        return None, (
            f"Veo error: {e}"
        )


# =========================================================
# LOGIN / SIGNUP SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="text-align:center">

        <h1>🎬 Nexa Video AI</h1>

        <p style="font-size:20px">
        Turn your ideas into AI videos
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    login_tab, signup_tab = st.tabs(
        [
            "🔑 Login",
            "📝 Sign Up"
        ]
    )

    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader(
            "Welcome Back"
        )

        email = st.text_input(
            "📧 Email",
            key="login_email"
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔑 Login",
            type="primary",
            use_container_width=True
        ):

            if not FIREBASE_API_KEY:

                st.error(
                    "Firebase API key is missing."
                )

            elif not email or not password:

                st.warning(
                    "Enter email and password."
                )

            else:

                result = firebase_login(
                    email,
                    password
                )

                if "idToken" in result:

                    st.session_state.logged_in = True

                    st.session_state.user_email = (
                        result.get(
                            "email",
                            email
                        )
                    )

                    st.session_state.id_token = (
                        result["idToken"]
                    )

                    st.rerun()

                else:

                    error = (
                        result
                        .get("error", {})
                        .get(
                            "message",
                            "Login failed."
                        )
                    )

                    st.error(
                        f"Login failed: {error}"
                    )

    # =====================================================
    # SIGNUP
    # =====================================================

    with signup_tab:

        st.subheader(
            "Create Your Account"
        )

        email = st.text_input(
            "📧 Email",
            key="signup_email"
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "🔒 Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "📝 Create Account",
            type="primary",
            use_container_width=True
        ):

            if not FIREBASE_API_KEY:

                st.error(
                    "Firebase API key is missing."
                )

            elif not email or not password:

                st.warning(
                    "Enter email and password."
                )

            elif password != confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain "
                    "at least 6 characters."
                )

            else:

                result = firebase_signup(
                    email,
                    password
                )

                if "idToken" in result:

                    st.session_state.logged_in = True

                    st.session_state.user_email = (
                        result.get(
                            "email",
                            email
                        )
                    )

                    st.session_state.id_token = (
                        result["idToken"]
                    )

                    st.rerun()

                else:

                    error = (
                        result
                        .get("error", {})
                        .get(
                            "message",
                            "Signup failed."
                        )
                    )

                    st.error(
                        f"Signup failed: {error}"
                    )

    st.divider()

    st.caption(
        "🔐 Secure authentication powered by Firebase"
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🎬 Nexa Video AI"
)

st.sidebar.write(
    f"👤 {st.session_state.user_email}"
)

st.sidebar.divider()

st.sidebar.subheader(
    "💎 Premium"
)

st.sidebar.write(
    "₹10 / month"
)

st.sidebar.write(
    "🎬 Up to 2 videos per day"
)

st.sidebar.write(
    f"Today: {st.session_state.videos_today}/2"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.generated_script = ""
    st.session_state.video_path = ""
    st.session_state.videos_today = 0

    st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "🎬 Nexa Video AI"
)

st.write(
    "Create AI-powered videos from text."
)

st.divider()


# =========================================================
# VIDEO IDEA
# =========================================================

st.subheader(
    "✍️ Video Idea"
)

idea = st.text_area(
    "Enter your video idea",
    height=160,
    placeholder=(
        "Example: A student who fails many times "
        "but finally achieves his dream."
    )
)


# =========================================================
# SETTINGS
# =========================================================

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
            "Marathi",
            "Gujarati",
            "Punjabi",
            "Urdu"
        ]
    )

with col2:

    duration = st.selectbox(
        "⏱️ Target Duration",
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
        "📱 Format",
        [
            "9:16",
            "16:9"
        ]
    )


style = st.selectbox(
    "🎨 Visual Style",
    [
        "Cinematic",
        "Realistic",
        "Documentary",
        "Educational",
        "Motivational",
        "Storytelling",
        "Animation"
    ]
)


# =========================================================
# SAFETY NOTICE
# =========================================================

st.info(
    "🛡️ Nexa does not support pornography, "
    "adult sexual content, explicit sexual content, "
    "or NSFW video generation."
)


# =========================================================
# GENERATE SCRIPT
# =========================================================

if st.button(
    "📝 Generate AI Script",
    type="primary",
    use_container_width=True
):

    if not idea.strip():

        st.warning(
            "Please enter a video idea."
        )

    elif is_unsafe_content(idea):

        st.error(
            "🚫 This content is not supported."
        )

    else:

        prompt = f"""
You are Nexa Video AI.

Create a production-ready video script.

Topic:
{idea}

Language:
{language}

Target duration:
{duration}

Voice:
{voice}

Visual style:
{style}

Aspect ratio:
{aspect_ratio}

Create 10 detailed scenes.

For each scene include:

1. Scene number
2. Approximate duration
3. Visual description
4. Video-generation prompt
5. Narration
6. On-screen text
7. Camera movement
8. Audio/music suggestion

The final video should feel cinematic,
professional and engaging.

Use the requested language for narration.

Safety:
Do not create pornography, adult sexual content,
explicit sexual content, erotic content, NSFW content,
or sexualized nudity.
"""

        with st.spinner(
            "🧠 Gemini is writing your script..."
        ):

            script, error = generate_script(
                prompt
            )

        if error:

            st.error(
                error
            )

        elif script:

            st.session_state.generated_script = script

            st.success(
                "✅ Script generated!"
            )

        else:

            st.error(
                "No script was returned."
            )


# =========================================================
# DISPLAY SCRIPT
# =========================================================

if st.session_state.generated_script:

    st.divider()

    st.subheader(
        "📝 Generated Script"
    )

    st.text_area(
        "Script",
        st.session_state.generated_script,
        height=500
    )

    st.download_button(
        "⬇️ Download Script",
        data=st.session_state.generated_script,
        file_name="nexa_video_script.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🎬 Create Video"
    )

    st.write(
        "Veo will create a cinematic video scene "
        "from your generated script."
    )

    if st.button(
        "🎬 Generate Video",
        type="primary",
        use_container_width=True
    ):

        if st.session_state.videos_today >= 2:

            st.error(
                "⛔ Daily video limit reached."
            )

        elif is_unsafe_content(
            st.session_state.generated_script
        ):

            st.error(
                "🚫 This script cannot be converted "
                "into a video."
            )

        else:

            video_prompt = f"""
Create a cinematic video based on this script:

{st.session_state.generated_script}

Language:
{language}

Visual style:
{style}

Aspect ratio:
{aspect_ratio}

Create natural cinematic motion,
professional camera movement,
realistic lighting and appropriate
background audio.

The content must be safe for a general audience.

Do not include pornography, adult sexual content,
explicit sexual content, erotic content,
NSFW content, or sexualized nudity.
"""

            with st.spinner(
                "🎬 Veo is generating your video..."
            ):

                video_path, error = (
                    generate_veo_video(
                        video_prompt,
                        aspect_ratio
                    )
                )

            if error:

                st.error(
                    error
                )

            elif video_path:

                st.session_state.video_path = (
                    video_path
                )

                st.session_state.videos_today += 1

                st.success(
                    "🎉 Video generated successfully!"
                )


# =========================================================
# VIDEO PLAYER + DOWNLOAD
# =========================================================

if st.session_state.video_path:

    st.divider()

    st.subheader(
        "🎥 Your Video"
    )

    st.video(
        st.session_state.video_path
    )

    try:

        with open(
            st.session_state.video_path,
            "rb"
        ) as video_file:

            video_data = video_file.read()

        st.download_button(
            "⬇️ Download MP4",
            data=video_data,
            file_name="nexa_video.mp4",
            mime="video/mp4",
       use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Could not prepare download: {e}"
        )


# =========================================================
# PREMIUM
# =========================================================

st.divider()

st.subheader(
    "💎 Nexa Premium"
)

left, right = st.columns(2)

with left:

    st.markdown(
        """
### ₹10 / month

- 🎬 Up to 2 videos per day
- ⏱️ 5+ minute target videos
- 🌐 Multiple languages
- 🎙️ AI narration
- 🎨 Cinematic AI visuals
- 📝 AI scripts
- 🎵 Generated audio
- ⬇️ MP4 download
- 🛡️ Safe content generation
"""
    )

with right:

    st.info(
        "Google Play Billing will be connected "
        "before publishing the app."
    )

    st.button(
        "💳 Upgrade to Premium",
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎬 Nexa Video AI • Turn Words Into Videos"
)

st.caption(
    "🔐 Firebase • 🤖 Gemini • 🎥 Veo"
            )
