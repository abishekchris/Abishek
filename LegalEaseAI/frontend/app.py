import os
import sys
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.formatters import (
    format_docx,
    format_html_preview,
    format_pdf,
)


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

APP_NAME = os.getenv(
    "APP_NAME",
    "LegalEase"
)


# =========================================================
# STREAMLIT PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "editing" not in st.session_state:
    st.session_state.editing = False


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main application container */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Legal document preview */
    .legal-card {
        background: #111827;
        color: #f3f4f6;
        border-radius: 14px;
        padding: 28px;
        border: 1px solid #374151;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }

    .legal-card h3 {
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
        color: #ffffff;
    }

    .legal-card p {
        margin: 0.5rem 0;
    }

    .spacer {
        height: 0.4rem;
    }

    /* Application title */
    .app-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    /* Small information card */
    .info-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        background: #f9fafb;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# APPLICATION HEADER
# =========================================================

st.markdown(
    '<div class="app-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-subtitle">'
    'AI-powered legal document drafting and export'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# LEGAL DISCLAIMER
# =========================================================

st.warning(
    "LegalEase creates AI-assisted legal document drafts "
    "for informational purposes only. It is not a law firm "
    "and generated content is not legal advice. Important "
    "documents should be reviewed by a qualified legal "
    "professional."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚖️ LegalEase")

    st.markdown(
        """
        ### About

        LegalEase uses Generative AI to create
        customizable legal document drafts.

        ### Supported workflow

        1. Enter document details
        2. Generate the document
        3. Review the document
        4. Edit if required
        5. Export as TXT, DOCX or PDF
        """
    )

    st.divider()

    st.caption(
        "AI-assisted document drafting"
    )


# =========================================================
# MAIN LAYOUT
# =========================================================

left_column, right_column = st.columns(
    [0.9, 1.1],
    gap="large",
)


# =========================================================
# LEFT COLUMN — DOCUMENT INPUT
# =========================================================

with left_column:

    st.subheader("Document Details")

    # -----------------------------------------------------
    # Document type
    # -----------------------------------------------------

    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "e.g. Non-Disclosure Agreement, "
            "Employment Contract, Lease Agreement"
        ),
    )

    # -----------------------------------------------------
    # Parties
    # -----------------------------------------------------

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Alice Johnson (Employee)\n"
            "TechNova Solutions Pvt. Ltd. (Employer)"
        ),
        height=130,
    )

    # -----------------------------------------------------
    # Terms
    # -----------------------------------------------------

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Example:\n"
            "Payment will be made monthly.\n"
            "Confidential information must not be disclosed.\n"
            "Either party may terminate with 30 days notice."
        ),
        height=200,
    )

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    dates = st.text_input(
        "Effective Date / Dates",
        placeholder="e.g. October 1, 2026",
    )

    st.write("")

    # -----------------------------------------------------
    # Generate button
    # -----------------------------------------------------

    generate_button = st.button(
        "⚡ Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate_button:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }

        # -------------------------------------------------
        # Frontend validation
        # -------------------------------------------------

        if not all(
            isinstance(value, str) and value.strip()
            for value in payload.values()
        ):

            st.error(
                "Please complete all document fields "
                "before generating."
            )

        else:

            # ---------------------------------------------
            # Send request to FastAPI
            # ---------------------------------------------

            with st.spinner(
                "Generating your legal document..."
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=120,
                    )

                    # -------------------------------------
                    # Successful response
                    # -------------------------------------

                    if response.ok:

                        data = response.json()

                        st.session_state.generated_text = (
                            data["content"]
                        )

                        st.session_state.editing = False

                        st.success(
                            "Document generated successfully."
                        )

                    # -------------------------------------
                    # Backend returned an error
                    # -------------------------------------

                    else:

                        try:

                            error_data = response.json()

                            detail = error_data.get(
                                "detail",
                                response.text,
                            )

                        except Exception:

                            detail = response.text

                        st.error(
                            f"Backend error: {detail}"
                        )

                # -----------------------------------------
                # Backend connection error
                # -----------------------------------------

                except requests.ConnectionError:

                    st.error(
                        "Could not connect to the LegalEase "
                        "backend.\n\n"
                        f"Make sure FastAPI is running at:\n"
                        f"{BACKEND_URL}"
                    )

                # -----------------------------------------
                # Request timeout
                # -----------------------------------------

                except requests.Timeout:

                    st.error(
                        "The document-generation request "
                        "timed out. Please try again."
                    )

                # -----------------------------------------
                # Other request errors
                # -----------------------------------------

                except requests.RequestException as exc:

                    st.error(
                        f"Request failed: {exc}"
                    )


# =========================================================
# RIGHT COLUMN — DOCUMENT PREVIEW
# =========================================================

with right_column:

    st.subheader("Document Preview")

    # =====================================================
    # NO DOCUMENT GENERATED
    # =====================================================

    if not st.session_state.generated_text:

        st.info(
            "Your generated document will appear here."
        )

        st.markdown(
            """
            <div class="info-card">

            <strong>How it works</strong>

            <br><br>

            Enter the document details on the left and
            click <strong>Generate Document</strong>.

            LegalEase will send the information to the
            FastAPI backend, which uses Gemini to generate
            the document.

            </div>
            """,
            unsafe_allow_html=True,
        )


    # =====================================================
    # DOCUMENT EXISTS
    # =====================================================

    else:

        # =================================================
        # EDITING MODE
        # =================================================

        if st.session_state.editing:

            edited_text = st.text_area(
                "Edit Document",
                value=st.session_state.generated_text,
                height=600,
                label_visibility="collapsed",
            )

            st.session_state.generated_text = edited_text

            if st.button(
                "✅ Finish Editing",
                use_container_width=True,
            ):

                st.session_state.editing = False

                st.rerun()


        # =================================================
        # PREVIEW MODE
        # =================================================

        else:

            preview = format_html_preview(
                st.session_state.generated_text
            )

            st.markdown(
                f"""
                <div class="legal-card">
                    {preview}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

            if st.button(
                "✏️ Edit Document",
                use_container_width=True,
            ):

                st.session_state.editing = True

                st.rerun()


        # =================================================
        # DOWNLOAD SECTION
        # =================================================

        st.divider()

        st.subheader("Download Document")

        content = st.session_state.generated_text

        # -------------------------------------------------
        # Generate DOCX
        # -------------------------------------------------

        docx_bytes = format_docx(
            content,
            document_type or "Legal Document",
        )

        # -------------------------------------------------
        # Generate PDF
        # -------------------------------------------------

        pdf_bytes = format_pdf(
            content,
            document_type or "Legal Document",
        )

        # -------------------------------------------------
        # Download buttons
        # -------------------------------------------------

        download_1, download_2, download_3 = st.columns(3)

        # TXT
        with download_1:

            st.download_button(
                "📄 Download TXT",
                data=content.encode("utf-8"),
                file_name="legalease_document.txt",
                mime="text/plain",
                use_container_width=True,
            )

        # DOCX
        with download_2:

            st.download_button(
                "📝 Download DOCX",
                data=docx_bytes,
                file_name="legalease_document.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        # PDF
        with download_3:

            st.download_button(
                "📕 Download PDF",
                data=pdf_bytes,
                file_name="legalease_document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "LegalEase • FastAPI + Streamlit + Google Gemini"
)