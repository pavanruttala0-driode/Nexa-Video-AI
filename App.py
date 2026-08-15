import requests
import streamlit as st


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
# GEMINI SETTINGS
# =========================================================

GEMINI_INTERACTIONS_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)

PREFERRED_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview"
]


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
# CONTENT SAFETY
# =========================================================

def is_unsafe_content(text):

    blocked_terms = [
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
        "18+ video",
        "18 plus video",
        "nsfw",
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
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signUp?key={FIREBASE_API_KEY}"
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
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signInWithPassword?key={FIREBASE_API_KEY}"
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
# FIND AVAILABLE GEMINI MODEL
# =========================================================

def find_gemini_model():

    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is missing."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models"
    )

    headers = {
        "x-goog-api-key": GEMINI_API_KEY
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        data = response.json()

        if response.status_code != 200:

            return None, str(data)

        available_models = []

        for model in data.get("models", []):

            name = model.get("name", "")

            supported_methods = model.get(
                "supportedGenerationMethods",
                []
            )

            if (
                "generateContent" in supported_methods
                or name.startswith("models/gemini")
            ):

                clean_name = name.replace(
                    "models/",
                    ""
                )

                available_models.append(
                    clean_name
                )

        for preferred in PREFERRED_MODELS:

            if preferred in available_models:

                return preferred, None

        # Fallback: find a Flash model
        for model in available_models:

            if "flash" in model.lower():

                return model, None

        return None, (
            "No suitable Gemini Flash model is available "
            "for this API key."
        )

    except Exception as e:

        return None, str(e)


# =========================================================
# GENERATE GEMINI SCRIPT
# =========================================================

def generate_gemini_script(prompt):

    if not GEMINI_API_KEY:

        return None, "GEMINI_API_KEY is not configured."

    model, model_error = find_gemini_model()

    if not model:

        return None, model_error

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "input": prompt
    }

    try:

        response = requests.post(
            GEMINI_INTERACTIONS_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        data = response.json()

        if response.status_code >= 400:

            return None, (
                f"Gemini API error {response.status_code}: "
                f"{data}"
            )

        # Current Interactions API normally returns output_text
        output_text = data.get(
            "output_text"
        )

        if output_text:

            return output_text, None

        # Backup parser
        outputs = data.get(
            "outputs",
            []
        )

        collected_text = []

        for item in outputs:

            if isinstance(item, dict):

                text = item.get(
                    "text"
                )

                if text:
                    collected_text.append(text)

                content = item.get(
                    "content",
                    []
                )

                if isinstance(content, list):

                    for part in content:

                        if isinstance(part, dict):

                            part_text = part.get(
                                "text"
                            )

                            if part_text:
                                collected_text.append(
                                    part_text
                                )

        if collected_text:

            return "\n".join(
                collected_text
            ), None

        return None, (
            "Gemini returned a response, "
            "but no text was found."
        )

    except requests.exceptions.Timeout:

        return None, (
            "Gemini request timed out. "
            "Please try again."
        )

    except Exception as e:

        return None, str(e)


# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="text-align:center">

        <h1>🎬 Nexa Video AI</h1>

        <p style="font-size:20px">
        Turn your ideas into AI-powered videos
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

        st.subheader(
            "Welcome Back"
        )

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
                    "Enter your email."
                )

            elif not login_password:

                st.warning(
                    "Enter your password."
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
                            "Login successful!"
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

                except Exception as e:

                    st.error(
                        f"Connection error: {e}"
                    )


    # =====================================================
    # SIGNUP
    # =====================================================

    with signup_tab:

        st.subheader(
            "Create Your Account"
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
                    "Enter your email."
                )

            elif not signup_password:

                st.warning(
                    "Enter a password."
                )

            elif signup_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
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
                            "Account created successfully!"
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

                except Exception as e:

                    st.error(
                        f"Connection error: {e}"
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
    "Enter your video idea",
    height=180,
    placeholder=(
        "Example: A student who fails many times "
        "but finally achieves his dream through "
        "hard work."
    )
)


# =========================================================
# VIDEO SETTINGS
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
        "⏱️ Duration",
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
            "9:16 Portrait",
            "16:9 Landscape",
            "1:1 Square"
        ]
    )


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
    "🛡️ Adult, pornographic, sexually explicit "
    "and NSFW video generation is not supported."
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

    if not text.strip():

        st.warning(
            "Please enter a video idea first."
        )

    elif is_unsafe_content(text):

        st.error(
            "🚫 This type of content is not supported "
            "by Nexa Video AI."
        )

    elif not GEMINI_API_KEY:

        st.error(
            "Gemini API key is missing."
        )

    else:

        prompt = f"""
You are the safe AI scriptwriter for Nexa Video AI.

SAFETY RULES:

Do not create:
- pornography
- adult videos
- sexually explicit content
- erotic sexual content
- NSFW content
- sexualized nudity
- sexual content involving minors

The video must be suitable for a general audience.

USER IDEA:
{text}

LANGUAGE:
{language}

TARGET DURATION:
{duration}

VOICE:
{voice}

VIDEO STYLE:
{style}

VIDEO FORMAT:
{aspect_ratio}

BACKGROUND MUSIC:
{music}

Create a detailed production-ready video script.

Divide the video into scenes.

For every scene provide:

1. Scene number
2. Scene duration
3. Visual description
4. AI visual prompt
5. Narration
6. On-screen text
7. Camera movement
8. Music suggestion

Make the narration natural in the selected language.

The final script should be suitable for converting into
a 5-minute or longer AI video.

Do not include adult or sexually explicit content.
"""

        with st.spinner(
            "🧠 Gemini is creating your script..."
        ):

            generated_text, error = (
                generate_gemini_script(
                    prompt
                )
            )

        if error:

            st.error(
                f"❌ {error}"
            )

        elif not generated_text:

            st.error(
                "Gemini returned an empty response."
            )

        elif is_unsafe_content(
            generated_text
        ):

            st.error(
                "🚫 Generated content failed "
                "the Nexa safety check."
            )

            st.session_state.generated_script = ""

        else:

            st.session_state.generated_script = (
                generated_text
            )

            st.success(
                "✅ AI script generated successfully!"
            )


# =========================================================
# SCRIPT RESULT
# =========================================================

if st.session_state.generated_script:

    st.divider()

    st.subheader(
        "📝 Generated AI Script"
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
        "🎬 Video Generation"
    )

    st.info(
        "The script is ready. In the next stage we will "
        "connect the actual video-generation engine."
    )

    st.button(
        "🎬 Generate Video",
        use_container_width=True
    )


# =========================================================
# PREMIUM
# =========================================================

st.divider()

st.subheader(
    "💎 Nexa Premium"
)

col_a, col_b = st.columns(2)

with col_a:

    st.markdown(
        """
### 💎 ₹10 / month

- 🎬 Up to 2 videos per day
- ⏱️ Minimum 5-minute videos
- 🌐 Multiple languages
- 🎙️ AI narration
- 🎨 AI visuals
- 📝 Automatic subtitles
- 🎵 Background music
- ⬇️ Video download
- 🛡️ Safe content generation
        """
    )

with col_b:

    st.info(
        "Google Play Billing will be connected "
        "before Play Store release."
    )

    st.button(
        "💳 Upgrade to Premium",
        use_container_width=True
    )


# =========================================================
# CONTENT POLICY
# =========================================================

st.divider()

st.subheader(
    "🛡️ Nexa Safety Policy"
)

st.write(
    """
Nexa Video AI is designed for general-audience content.

Adult, pornographic, sexually explicit, erotic,
and NSFW video generation is not supported.

Educational, motivational, storytelling, technology,
travel, history, entertainment and other safe topics
are supported.
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
    "🔐 Secure • 🌐 Multilingual • 🛡️ Safe AI"
)
