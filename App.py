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
# API SETTINGS
# =========================================================

FIREBASE_AUTH_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)

GEMINI_MODEL = "gemini-3.6-flash"


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "logged_in": False,
    "user_email": "",
    "id_token": "",
    "generated_script": "",
    "videos_today": 0,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


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
        "nsfw",
        "erotic",
        "sexual content",
        "sexual video",
        "sex video",
        "adult video",
        "adult content",
        "sexually explicit",
        "explicit sex",
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

    value = text.lower()

    return any(
        term in value
        for term in blocked_terms
    )


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
# GEMINI SCRIPT GENERATION
# =========================================================

def generate_script(prompt):

    if not GEMINI_API_KEY:

        return None, (
            "GEMINI_API_KEY is missing. "
            "Add it to Streamlit Secrets."
        )

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
            GEMINI_URL,
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

        # =================================================
        # READ INTERACTIONS API OUTPUT
        # =================================================

        output_text = data.get(
            "output_text"
        )

        if output_text:

            return output_text, None

        # Backup response parser

        collected = []

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

                    text = content.get(
                        "text",
                        ""
                    )

                    if text:
                        collected.append(
                            text
                        )

        if collected:

            return "\n".join(
                collected
            ), None

        return None, (
            "Gemini responded, but "
            "no generated text was found."
        )

    except requests.exceptions.Timeout:

        return None, (
            "Gemini request timed out. "
            "Please try again."
        )

    except Exception as e:

        return None, str(e)


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="text-align:center">

        <h1>🎬 Nexa Video AI</h1>

        <p>
        Create AI-powered videos from your ideas
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


    # =====================================================
    # SIGNUP
    # =====================================================

    with signup_tab:

        st.subheader(
            "Create Nexa Account"
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
            key="confirm_password"
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
                    "Password must be at least 6 characters."
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

                    st.success(
                        "Account created!"
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
        "🔐 Authentication powered by Firebase"
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
    f"🎬 Videos today: "
    f"{st.session_state.videos_today}/2"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.generated_script = ""
    st.session_state.videos_today = 0

    st.rerun()


# =========================================================
# MAIN APP
# =========================================================

st.title(
    "🎬 Nexa Video AI"
)

st.write(
    "Turn your text into multilingual AI video scripts."
)

st.divider()


# =========================================================
# INPUT
# =========================================================

st.subheader(
    "✍️ Video Idea"
)

idea = st.text_area(
    "What video do you want to create?",
    height=180,
    placeholder=(
        "Example: A student who fails many times "
        "but finally succeeds through hard work."
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

    ratio = st.selectbox(
        "📱 Format",
        [
            "9:16 Portrait",
            "16:9 Landscape",
            "1:1 Square"
        ]
    )


style = st.selectbox(
    "🎨 Style",
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
    "🎵 Music",
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
# SAFETY
# =========================================================

st.info(
    "🛡️ Adult, pornographic, sexually explicit "
    "and NSFW videos are not supported."
)


# =========================================================
# GENERATE
# =========================================================

if st.button(
    "🚀 Generate AI Script",
    type="primary",
    use_container_width=True
):

    if not idea.strip():

        st.warning(
            "Please enter a video idea."
        )

    elif is_unsafe_content(idea):

        st.error(
            "🚫 This type of content is not supported "
            "by Nexa Video AI."
        )

    elif st.session_state.videos_today >= 2:

        st.error(
            "⛔ Daily limit reached. "
            "Premium users can generate up to "
            "2 videos per day."
        )

    else:

        prompt = f"""
You are Nexa Video AI, a safe multilingual
AI video script generator.

Create a detailed {duration} video script.

Topic:
{idea}

Language:
{language}

Voice:
{voice}

Visual style:
{style}

Aspect ratio:
{ratio}

Music:
{music}

Create 8 to 12 scenes.

For each scene provide:

1. Scene number
2. Duration
3. Visual description
4. AI visual prompt
5. Narration
6. On-screen text
7. Camera movement
8. Music suggestion

Make the story engaging and natural.

The video must be suitable for a general audience.

Do not generate:
- pornography
- adult content
- sexual content
- erotic content
- NSFW content
- sexualized nudity
- sexual content involving minors

Create the narration in the selected language.
"""

        with st.spinner(
            "🧠 Creating your AI script..."
        ):

            script, error = generate_script(
                prompt
            )

        if error:

            st.error(
                f"❌ {error}"
            )

        elif not script:

            st.error(
                "No script was returned."
            )

        elif is_unsafe_content(script):

            st.error(
                "🚫 Generated content failed "
                "the safety check."
            )

        else:

            st.session_state.generated_script = script

            st.session_state.videos_today += 1

            st.success(
                "✅ Script generated successfully!"
            )


# =========================================================
# RESULT
# =========================================================

if st.session_state.generated_script:

    st.divider()

    st.subheader(
        "📝 Generated Script"
    )

    st.text_area(
        "AI Script",
        st.session_state.generated_script,
        height=550
    )

    st.download_button(
        "⬇️ Download Script",
        st.session_state.generated_script,
        file_name="nexa_video_script.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🎬 Video Generation"
    )

    st.info(
        "Your script is ready. "
        "The actual MP4 generation engine will be "
        "connected in the next stage."
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

🎬 2 videos per day

⏱️ 5+ minute videos

🌐 Multiple languages

🎙️ AI voice

🎨 AI visuals

📝 Subtitles

🎵 Background music

⬇️ Download
"""
    )

with right:

    st.info(
        "Google Play Billing will be connected "
        "before Play Store release."
    )

    st.button(
        "💳 Upgrade to Premium",
        use_container_width=True
    )


# =========================================================
# POLICY
# =========================================================

st.divider()

st.subheader(
    "🛡️ Content Policy"
)

st.write(
    """
Nexa Video AI is designed for general-audience content.

Adult, pornographic, sexually explicit, erotic,
and NSFW video generation is not supported.

Educational, motivational, technology, travel,
history, storytelling and other safe topics are supported.
"""
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎬 Nexa Video AI • Turn Words Into Videos"
    )
