import os
import re
import tempfile
import requests
import streamlit as st

from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Nexa Video AI",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# SECRETS
# =========================================================

FIREBASE_API_KEY = st.secrets.get(
    "FIREBASE_API_KEY", ""
)

GEMINI_API_KEY = st.secrets.get(
    "GEMINI_API_KEY", ""
)


# =========================================================
# API
# =========================================================

FIREBASE_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/interactions"
)

GEMINI_MODEL = "gemini-3.6-flash"


# =========================================================
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = ""

if "token" not in st.session_state:
    st.session_state.token = ""

if "script" not in st.session_state:
    st.session_state.script = ""

if "video" not in st.session_state:
    st.session_state.video = None


# =========================================================
# SAFETY
# =========================================================

def unsafe(text):

    blocked = [
        "porn",
        "pornography",
        "xxx",
        "nude",
        "nudity",
        "nsfw",
        "erotic",
        "adult video",
        "adult content",
        "sex video",
        "sexual content",
        "sexually explicit",
        "explicit sex",
        "onlyfans",

        "బూతు",
        "నగ్న",
        "అశ్లీల",
        "సెక్స్ వీడియో",

        "अश्लील",
        "नग्न",
        "सेक्स वीडियो"
    ]

    text = text.lower()

    return any(
        word in text
        for word in blocked
    )


# =========================================================
# FIREBASE
# =========================================================

def firebase_login(email, password):

    url = (
        f"{FIREBASE_URL}:signInWithPassword"
        f"?key={FIREBASE_API_KEY}"
    )

    r = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        },
        timeout=30
    )

    return r.json()


def firebase_signup(email, password):

    url = (
        f"{FIREBASE_URL}:signUp"
        f"?key={FIREBASE_API_KEY}"
    )

    r = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        },
        timeout=30
    )

    return r.json()


# =========================================================
# GEMINI
# =========================================================

def generate_script(topic, language, duration, style):

    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is missing."

    prompt = f"""
You are Nexa Video AI.

Create a safe, engaging video script.

Topic:
{topic}

Language:
{language}

Target duration:
{duration}

Style:
{style}

Create 10 scenes.

For every scene give:

SCENE 1
Duration:
Visual:
Narration:
On-screen text:

SCENE 2
Duration:
Visual:
Narration:
On-screen text:

Continue until SCENE 10.

Make the narration suitable for a general audience.

Do not create pornography, sexual content,
adult content, erotic content, NSFW content,
or sexualized nudity.
"""

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": GEMINI_MODEL,
        "input": prompt
    }

    try:

        r = requests.post(
            GEMINI_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        data = r.json()

        if r.status_code >= 400:

            return None, str(data)

        text = data.get(
            "output_text"
        )

        if text:
            return text, None

        parts = []

        for step in data.get(
            "steps",
            []
        ):

            if step.get(
                "type"
            ) != "model_output":
                continue

            for content in step.get(
                "content",
                []
            ):

                if content.get(
                    "type"
                ) == "text":

                    value = content.get(
                        "text",
                        ""
                    )

                    if value:
                        parts.append(value)

        if parts:
            return "\n".join(parts), None

        return None, (
            "No text returned by Gemini."
        )

    except Exception as e:

        return None, str(e)


# =========================================================
# PARSE SCENES
# =========================================================

def parse_scenes(script):

    pattern = re.compile(
        r"SCENE\s+\d+"
        r"(.*?)(?=SCENE\s+\d+|$)",
        re.IGNORECASE |
        re.DOTALL
    )

    matches = pattern.findall(
        script
    )

    scenes = []

    for match in matches:

        text = match.strip()

        if text:
            scenes.append(text)

    return scenes


# =========================================================
# CREATE IMAGE
# =========================================================

def create_scene_image(
    text,
    number,
    width=720,
    height=1280
):

    image = Image.new(
        "RGB",
        (width, height),
        "black"
    )

    draw = ImageDraw.Draw(
        image
    )

    try:

        font = ImageFont.truetype(
            "DejaVuSans.ttf",
            38
        )

        small_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            28
        )

    except:

        font = ImageFont.load_default()
        small_font = font

    title = f"SCENE {number}"

    draw.text(
        (40, 50),
        title,
        fill="white",
        font=font
    )

    # Wrap text

    words = text.split()

    lines = []
    current = ""

    for word in words:

        test = (
            current + " " + word
        ).strip()

        if len(test) > 32:

            lines.append(
                current
            )

            current = word

        else:

            current = test

    if current:
        lines.append(
            current
        )

    y = 180

    for line in lines:

        draw.text(
            (40, y),
            line,
            fill="white",
            font=small_font
        )

        y += 50

        if y > height - 100:
            break

    path = os.path.join(
        tempfile.gettempdir(),
        f"nexa_scene_{number}.png"
    )

    image.save(path)

    return path


# =========================================================
# TEXT TO SPEECH
# =========================================================

def create_voice(
    text,
    language
):

    language_codes = {

        "English": "en",
        "Telugu": "te",
        "Hindi": "hi",
        "Tamil": "ta",
        "Malayalam": "ml",
        "Kannada": "kn",
        "Bengali": "bn",
        "Marathi": "mr",
        "Gujarati": "gu",
        "Punjabi": "pa",
        "Urdu": "ur"
    }

    code = language_codes.get(
        language,
        "en"
    )

    path = os.path.join(
        tempfile.gettempdir(),
        "nexa_voice.mp3"
    )

    try:

        tts = gTTS(
            text=text,
            lang=code
        )

        tts.save(path)

        return path, None

    except Exception as e:

        return None, str(e)


# =========================================================
# CREATE VIDEO
# =========================================================

def create_video(
    script,
    language,
    progress_bar
):

    scenes = parse_scenes(
        script
    )

    if not scenes:

        return None, (
            "Could not find scenes "
            "in the generated script."
        )

    # Limit first prototype
    scenes = scenes[:10]

    clips = []

    total = len(scenes)

    for index, scene in enumerate(
        scenes,
        start=1
    ):

        progress_bar.progress(
            int(
                ((index - 1) / total) * 90
            )
        )

        image_path = (
            create_scene_image(
                scene,
                index
            )
        )

        # Use scene text as narration.
        voice_path, error = (
            create_voice(
                scene,
                language
            )
        )

        if error:
            return None, error

        audio = AudioFileClip(
            voice_path
        )

        duration = max(
            audio.duration,
            2
        )

        clip = (
            ImageClip(image_path)
            .with_duration(duration)
            .with_audio(audio)
        )

        clips.append(clip)

    progress_bar.progress(95)

    final = concatenate_videoclips(
        clips,
        method="compose"
    )

    output = os.path.join(
        tempfile.gettempdir(),
        "nexa_video.mp4"
    )

    final.write_videofile(
        output,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    final.close()

    progress_bar.progress(100)

    return output, None


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.title(
        "🎬 Nexa Video AI"
    )

    st.write(
        "Turn your ideas into videos."
    )

    login, signup = st.tabs(
        [
            "🔑 Login",
            "📝 Sign Up"
        ]
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    with login:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Enter email and password."
                )

            elif not FIREBASE_API_KEY:

                st.error(
                    "Firebase API key missing."
                )

            else:

                result = firebase_login(
                    email,
                    password
                )

                if "idToken" in result:

                    st.session_state.logged_in = True

                    st.session_state.email = (
                        result.get(
                            "email",
                            email
                        )
                    )

                    st.session_state.token = (
                        result["idToken"]
                    )

                    st.rerun()

                else:

                    st.error(
                        result.get(
                            "error",
                            {}
                        ).get(
                            "message",
                            "Login failed."
                        )
                    )

    # -----------------------------------------------------
    # SIGNUP
    # -----------------------------------------------------

    with signup:

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Enter email and password."
                )

            elif password != confirm:

                st.error(
                    "Passwords don't match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                result = firebase_signup(
                    email,
                    password
                )

                if "idToken" in result:

                    st.session_state.logged_in = True

                    st.session_state.email = (
                        result.get(
                            "email",
                            email
                        )
                    )

                    st.session_state.token = (
                        result["idToken"]
                    )

                    st.rerun()

                else:

                    st.error(
                        result.get(
                            "error",
                            {}
                        ).get(
                            "message",
                            "Signup failed."
                        )
                    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🎬 Nexa Video AI"
)

st.sidebar.write(
    f"👤 {st.session_state.email}"
)

if st.sidebar.button(
    "🚪 Logout"
):

    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.token = ""

    st.rerun()


# =========================================================
# MAIN
# =========================================================

st.title(
    "🎬 Nexa Video AI"
)

st.write(
    "Create a video from your text idea."
)

st.divider()


# =========================================================
# INPUT
# =========================================================

topic = st.text_area(
    "✍️ What video do you want?",
    height=150,
    placeholder=(
        "Example: A student works hard "
        "and finally achieves his dream."
    )
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
            "Marathi",
            "Gujarati",
            "Punjabi",
            "Urdu"
        ]
    )

with col2:

    duration = st.selectbox(
        "⏱️ Video length",
        [
            "Short test",
            "5 minutes"
        ]
    )


style = st.selectbox(
    "🎨 Style",
    [
        "Cinematic",
        "Educational",
        "Motivational",
        "Documentary",
        "Storytelling"
    ]
)


# =========================================================
# SAFETY
# =========================================================

st.info(
    "🛡️ Adult, pornographic, sexually explicit "
    "and NSFW videos are not supported."
)


# =========================================================
# GENERATE SCRIPT
# =========================================================

if st.button(
    "🧠 Generate Script",
    type="primary",
    use_container_width=True
):

    if not topic.strip():

        st.warning(
            "Enter a video idea first."
        )

    elif unsafe(topic):

        st.error(
            "🚫 This content is not supported."
        )

    else:

        with st.spinner(
            "Gemini is creating your script..."
        ):

            script, error = generate_script(
                topic,
                language,
                duration,
                style
            )

        if error:

            st.error(error)

        else:

            st.session_state.script = script

            st.success(
                "✅ Script generated!"
            )


# =========================================================
# SCRIPT
# =========================================================

if st.session_state.script:

    st.divider()

    st.subheader(
        "📝 Your Script"
    )

    st.text_area(
        "Generated Script",
        st.session_state.script,
        height=500
    )

    st.download_button(
        "⬇️ Download Script",
        data=st.session_state.script,
        file_name="nexa_script.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🎬 Create MP4"
    )

    st.write(
        "This free prototype creates scene cards "
        "with multilingual narration and combines "
        "them into an MP4."
    )

    if st.button(
        "🎥 Create Video",
        type="primary",
        use_container_width=True
    ):

        if unsafe(
            st.session_state.script
        ):

            st.error(
                "🚫 Unsafe content detected."
            )

        else:

            progress = st.progress(0)

            with st.spinner(
                "🎬 Creating your video..."
            ):

                video, error = create_video(
                    st.session_state.script,
                    language,
                    progress
                )

            if error:

                st.error(
                    f"Video creation failed: {error}"
                )

            else:

                st.session_state.video = video

                st.success(
                    "🎉 Video created successfully!"
                )


# =========================================================
# VIDEO OUTPUT
# =========================================================

if st.session_state.video:

    st.divider()

    st.subheader(
        "🎥 Your Video"
    )

    st.video(
        st.session_state.video
    )

    with open(
        st.session_state.video,
        "rb"
    ) as file:

        video_data = file.read()

    st.download_button(
        "⬇️ Download MP4",
        data=video_data,
        file_name="nexa_video.mp4",
        mime="video/mp4",
        use_container_width=True
    )


# =========================================================
# PREMIUM
# =========================================================

st.divider()

st.subheader(
    "💎 Nexa Premium"
)

st.markdown(
    """
### ₹10 / month

- 🎬 Video creation
- 🌐 Multiple languages
- 📝 AI scripts
- 🎙️ AI narration
- ⬇️ MP4 download
- 🛡️ Safe content generation
"""
)

st.info(
    "Google Play subscription will be connected "
    "after the core video pipeline is working."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎬 Nexa Video AI • Turn Words Into Videos"
    )
