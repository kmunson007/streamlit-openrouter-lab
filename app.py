import os
import json
import html
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError


# -----------------------------
# Configuration
# -----------------------------

MODEL = "openrouter/auto"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY is not set.")
    st.stop()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-OpenRouter-Title": "Ken's AI Assistant",
    },
)


# -----------------------------
# Helper: copyable text box
# -----------------------------

def copy_box(label, text, height=350, max_text_height=260):
    """
    Displays text in a box with a visible Copy button.
    The text area scrolls if the answer is long.
    """

    safe_label = html.escape(label)
    safe_text_for_display = html.escape(text)
    safe_text_for_js = json.dumps(text)

    components.html(
        f"""
        <div style="
            font-family: sans-serif;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            background-color: #f8f9fa;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            ">
                <strong style="font-size: 1.1rem;">{safe_label}</strong>

                <button
                    id="copy-button"
                    style="
                        border: 1px solid #ccc;
                        border-radius: 8px;
                        padding: 6px 14px;
                        cursor: pointer;
                        background-color: white;
                        font-size: 0.95rem;
                    "
                >
                    Copy
                </button>
            </div>

            <div style="
                white-space: pre-wrap;
                line-height: 1.55;
                color: #222;
                max-height: {max_text_height}px;
                overflow-y: auto;
                padding-right: 8px;
            ">{safe_text_for_display}</div>
        </div>

        <script>
            const textToCopy = {safe_text_for_js};
            const button = document.getElementById("copy-button");

            button.addEventListener("click", async () => {{
                await navigator.clipboard.writeText(textToCopy);
                button.innerText = "Copied!";
                setTimeout(() => {{
                    button.innerText = "Copy";
                }}, 1200);
            }});
        </script>
        """,
        height=height,
    )

# -----------------------------
# Streamlit UI
# -----------------------------

st.title("Ken's AI Assistant")

cost_quality_tradeoff = st.slider(
    "OpenRouter cost/quality tradeoff",
    min_value=0,
    max_value=10,
    value=9,
    help="0 = highest quality, 10 = lowest cost",
)

with st.form("chat_form"):
    user_input = st.text_area("Ask me anything:", height=120)
    submitted = st.form_submit_button("Ask")


# -----------------------------
# Model call
# -----------------------------

if submitted and user_input.strip():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": user_input}
            ],
            extra_body={
                "plugins": [
                    {
                        "id": "auto-router",
                        "cost_quality_tradeoff": cost_quality_tradeoff,
                    }
                ]
            },
        )

        answer = response.choices[0].message.content

        copy_box(
            label="Question",
            text=user_input,
            height=180,
            max_text_height=90,
        )

        copy_box(
            label="Assistant response",
            text=answer,
            height=650,
            max_text_height=520,
        )

        st.caption(f"Requested model: {MODEL}")
        st.caption(f"Cost/quality tradeoff: {cost_quality_tradeoff}")
        st.caption(f"Actual model selected by OpenRouter: {response.model}")

    except AuthenticationError as e:
        st.error("Authentication failed. Check your OPENROUTER_API_KEY.")
        st.code(str(e))

    except RateLimitError as e:
        st.error("OpenRouter quota or rate-limit issue. Check your OpenRouter credits and key limits.")
        st.code(str(e))

    except APIError as e:
        st.error("API error from OpenRouter/OpenAI-compatible endpoint.")
        st.code(str(e))

    except Exception as e:
        st.error("Unexpected error.")
        st.code(str(e))

