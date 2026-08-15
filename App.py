    import os
import requests
import streamlit as st
from google import genai

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
# CONFIGURATION
# =========================================================

FIREBASE_API_KEY = st.secrets.get(
    "FIREBASE_API_KEY",
    ""
)

GEMINI_API_KEY = st.secrets.get(
    "GEMINI_API_KEY",
    ""
)

FIREBASE_AUTH_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)

# =========================================================
# GEMINI CLIENT
# =========================================================

gemini_client = None

if GEMINI_API_KEY:

    try:
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    except Exception:

        gemini_client = None


# =========================================================
# CONTENT SAFETY FILTER
# =========================================================

def is_unsafe_content(text):

    blocked_terms = [

        # English
        "porn",
        "pornography",
        "xxx",
        "nude",
        "nudity",
        "explicit sex",
        "sexual content",
        "sexual video",
        "sex video",
        "adult video",
        "adult content",
        "erotic",
        "sexually explicit",
        "sexual intercourse",

        # Common indirect requests
        "18+ video",
        "18 plus video",
        "nsfw",
        "onlyfans",

        # Telugu
        "బూతు",
        "నగ్న",
        "అశ్లీల",
        "సెక్స్ వీడియో",

        # Hindi
        "अश्लील",
        "नग्न",
        "सेक्स वीडियो",

        # Tamil
        "ஆபாச",
        "நிர்வாண",
        "செக்ஸ் வீடியோ"
    ]

    text_lower = text.lower()

    for term in blocked_terms:

        if term in text_lower:
            return True

    return False


# =========================================================
# FIREBASE SIGNUP
# =========================================================

def firebase_signup(email, password):

    url = (
        f"{FIREBASE_AUTH_URL}:signUp"
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
        f"{FIREBASE_AUTH_URL}:signInWithPassword"
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


# =========================================================
# LOGIN / SIGNUP SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="text-align:center;">

        <h1>🎬 Nexa Video AI</h1>

        <p style="font-size:20px;">
        Turn your words into AI-powered videos
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    login_tab, signup_tab = st.tabs(
        [
            "🔑 Login",
            "📝 Create Account"
        ]
    )

    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("Welcome Back")

        login_email = st.text_input(
            "📧 Email",
            key="login_email"
        )

        login_password = st.text_input(
            "🔒 Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔑 Login",
            use_container_width=True,
            type="primary"
        ):

            if not FIREBASE_API_KEY:

                st.error(
                    "Firebase API key is not configured."
                )

            elif not login_email:

                st.warning(
                    "Please enter your email."
                )

            elif not login_password:

                st.warning(
                    "Please enter your password."
                )

            else:

                try:

                    result = firebase_login(
                        login_email,
                        login_password
                    )

                    if "idToken" in result:

                        st.session_state.logged_in = True

                        st.session_state.user_email = (
                            result.get(
                                "email",
                                login_email
                            )
                        )

                        st.session_state.id_token = (
                            result["idToken"]
                        )

                        st.success(
                            "✅ Login successful!"
                        )

                        st.rerun()

                    else:

                        error_message = (
                            result.get(
                                "error",
                                {}
                            ).get(
                                "message",
                                "Login failed."
                            )
                        )

                        st.error(
                            f"❌ Login failed: "
                            f"{error_message}"
                        )

                except Exception as e:

                    st.error(
                        f"Connection error: {e}"
                    )

    # =====================================================
    # SIGNUP
    # =====================================================

    with signup_tab:

        st.subheader(
            "Create Your Nexa Account"
        )

        signup_email = st.text_input(
            "📧 Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "🔒 Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True,
            type="primary"
        ):

            if not FIREBASE_API_KEY:

                st.error(
                    "Firebase API key is not configured."
                )

            elif not signup_email:

                st.warning(
                    "Please enter your email."
                )

            elif not signup_password:

                st.warning(
                    "Please enter a password."
                )

            elif signup_password != confirm_password:

                st.error(
                    "❌ Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "❌ Password must contain at least "
                    "6 characters."
                )

            else:

                try:

                    result = firebase_signup(
                        signup_email,
                        signup_password
                    )

                    if "idToken" in result:

                        st.session_state.logged_in = True

                        st.session_state.user_email = (
                            result.get(
                                "email",
                                signup_email
                            )
                        )

                        st.session_state.id_token = (
                            result["idToken"]
                        )

                        st.success(
                            "✅ Account created!"
                        )

                        st.rerun()

                    else:

                        error_message = (
                            result.get(
                                "error",
                                {}
                            ).get(
                                "message",
                                "Signup failed."
                            )
                        )

                        st.error(
                            f"❌ Signup failed: "
                            f"{error_message}"
                        )

                except Exception as e:

                    st.error(
                        f"Connection error: {e}"
                    )

    st.divider()

    st.caption(
        "🔐 Account authentication is handled by Firebase."
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
    "🎬 Maximum 2 videos per day"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False

    st.session_state.user_email = ""

    st.session_state.id_token = ""

    st.session_state.generated_script = ""

    st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "🎬 Nexa Video AI"
)

st.write(
    "Create multilingual AI-powered videos "
    "from your ideas."
)

st.divider()


# =========================================================
# VIDEO IDEA
# =========================================================

st.subheader(
    "✍️ Create Your Video"
)

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
# LANGUAGE + DURATION
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


# =========================================================
# VOICE + FORMAT
# =========================================================

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
        "Educational",
        "Documentary",
        "Motivational",
        "Storytelling",
        "Cartoon",
        "Anime"
    ]
)


# =========================================================
# BACKGROUND MUSIC
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


# =========================================================
# SAFETY NOTICE
# =========================================================

st.info(
    "🛡️ Nexa Video AI does not support adult, "
    "pornographic, sexually explicit, or NSFW videos."
)


# =========================================================
# GENERATE SCRIPT
# =========================================================

st.divider()

if st.button(
    "🚀 Generate AI Script",
    use_container_width=True,
    type="primary"
):

    # -----------------------------------------------------
    # EMPTY INPUT
    # -----------------------------------------------------

    if not text.strip():

        st.warning(
            "⚠️ Please enter your video idea first."
        )

    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------

    elif is_unsafe_content(text):

        st.error(
            "🚫 This type of content is not supported "
            "by Nexa Video AI.\n\n"
            "Please enter a safe topic such as education, "
            "stories, motivation, travel, technology, "
            "history, or entertainment."
        )

    # -----------------------------------------------------
    # GEMINI CHECK
    # -----------------------------------------------------

    elif gemini_client is None:

        st.error(
            "🤖 Gemini API is not configured.\n\n"
            "Please add GEMINI_API_KEY to "
            "Streamlit Secrets."
        )

    # -----------------------------------------------------
    # GENERATION
    # -----------------------------------------------------

    else:

        prompt = f"""
You are the safe AI scriptwriter for Nexa Video AI.

IMPORTANT SAFETY RULES:

Do not create adult, pornographic, sexually explicit,
NSFW, or sexualized content.

Do not create sexual content involving minors.

If the user's request asks for prohibited sexual content,
do not generate it.

Instead, return exactly:

"CONTENT_NOT_SUPPORTED"

USER VIDEO IDEA:

{text}

LANGUAGE:

{language}

TARGET DURATION:

{duration}

VOICE:

{voice}

VIDEO STYLE:

{style}

ASPECT RATIO:

{aspect_ratio}

BACKGROUND MUSIC:

{music}

Create a production-ready video script.

Divide the video into scenes.

For every scene provide:

1. Scene number
2. Narration
3. Visual description
4. Suggested duration
5. On-screen text
6. Background music suggestion

Make the narration natural and suitable for the selected
language.

The final result will later be used to create an AI video.

Keep the content suitable for a general audience.
"""

        try:

            with st.spinner(
                "🧠 Gemini is creating your safe AI script..."
            ):

                response = (
                    gemini_client
                    .models
                    .generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                )

            generated_text = response.text.strip()

            # ------------------------------------------------
            # SECOND SAFETY CHECK
            # ------------------------------------------------

            if (
                generated_text
                == "CONTENT_NOT_SUPPORTED"
            ):

                st.error(
                    "🚫 This request cannot be generated "
                    "by Nexa Video AI."
                )

                st.session_state.generated_script = ""

            elif is_unsafe_content(
                generated_text
            ):

                st.error(
                    "🚫 The generated content did not "
                    "pass Nexa Video AI safety checks."
                )

                st.session_state.generated_script = ""

            else:

                st.session_state.generated_script = (
                    generated_text
                )

                st.success(
                    "✅ Safe AI script generated!"
                )

        except Exception as e:

            st.error(
                f"Gemini API error: {e}"
            )


# =========================================================
# GENERATED SCRIPT
# =========================================================

if st.session_state.generated_script:

    st.divider()

    st.subheader(
        "📝 Your AI Video Script"
    )

    st.text_area(
        "Generated Script",
        st.session_state.generated_script,
        height=500
    )

    st.download_button(
        label="⬇️ Download Script",
        data=st.session_state.generated_script,
        file_name="nexa_video_script.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🎬 Video Generation"
    )

    st.info(
        "Your script is ready. The next stage will "
        "generate the visual scenes, voice narration, "
        "subtitles, background music, and final MP4."
    )

    st.button(
        "🎬 Create Video",
        use_container_width=True
    )


# =========================================================
# PREMIUM PLAN
# =========================================================

st.divider()

st.subheader(
    "💎 Nexa Premium"
)

premium_col1, premium_col2 = st.columns(2)

with premium_col1:

    st.markdown(
        """
### 💎 ₹10 / month

- 🎬 Maximum 2 videos per day
- ⏱️ 5+ minute videos
- 🌐 Multiple languages
- 🎙️ AI voice narration
- 🎨 AI visuals
- 📝 Automatic subtitles
- 🎵 Background music
- ⬇️ Video download
- 🛡️ Safe content generation
        """
    )

with premium_col2:

    st.info(
        "Google Play Billing will be connected "
        "when we build the Android version."
    )

    st.button(
        "💳 Upgrade to Premium",
        use_container_width=True
    )


# =========================================================
# SAFETY POLICY
# =========================================================

st.divider()

st.subheader(
    "🛡️ Content Policy"
)

st.write(
    """
Nexa Video AI is designed for general-audience content.

Adult, pornographic, sexually explicit, and NSFW
video generation is not supported.

Users should create educational, informational,
creative, motivational, entertainment, travel,
technology, storytelling, and other safe content.
"""
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎬 Nexa Video AI • Turn Words Into Videos"
)

st.caption(
    "🛡️ Safe AI • 🔐 Secure Accounts • 🌐 Multilingual"
)
