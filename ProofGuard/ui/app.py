"""
ProofGuard - Streamlit Frontend & Intelligence Dashboard
Author: Vignesh (Initial Frontend Responsibility) / Integration

Ticket 1 Deliverable: Document Upload, OCR Processing Preview,
Product Information Extraction, CPSC Recall Preview, and System Dashboard.
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from app.db.init_db import init_db
from app.db.database import SessionLocal
from app.ocr.document_processor import extract_text
from app.extraction.product_extractor import extract_product_info
from app.services.document_service import (
    save_processed_document,
    get_dashboard_metrics,
    get_recent_documents,
    get_recent_products,
    get_available_recalls,
)

# Page Configuration
st.set_page_config(
    page_title="ProofGuard — Product Intelligence & Recall Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure database tables exist
init_db()

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-success { background: #DCFCE7; color: #166534; }
    .badge-info { background: #DBEAFE; color: #1E40AF; }
    .badge-warning { background: #FEF3C7; color: #92400E; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.sidebar.title("ProofGuard")
    st.sidebar.caption("Evidence-Based Recall Intelligence")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📄 Document Upload & Extraction",
            "🔍 CPSC Recall Intelligence",
            "ℹ️ Architecture & About",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    st.sidebar.markdown("🟢 **Database:** SQLite Connected")
    st.sidebar.markdown("🟢 **OCR Engine:** PyMuPDF + Tesseract")
    st.sidebar.markdown("🟢 **NLP Pipeline:** spaCy `en_core_web_sm`")
    st.sidebar.markdown("🟢 **Recall Dataset:** 562 CPSC Records")

    st.sidebar.markdown("---")
    st.sidebar.caption("ProofGuard Academic Project • Ticket 1")
    return page


def page_dashboard():
    st.markdown('<div class="main-header">🛡️ ProofGuard System Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Cross-Document Product Identity & Evidence-Based Recall Intelligence — Ticket 1 Overview</div>',
        unsafe_allow_html=True,
    )

    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['uploaded_documents']}</div>
                <div class="metric-label">Uploaded Documents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['processed_documents']}</div>
                <div class="metric-label">Processed Documents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['products_extracted']}</div>
                <div class="metric-label">Extracted Products</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['recalls_available']}</div>
                <div class="metric-label">Available CPSC Recalls</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Recent Extracted Products", "📁 Recent Document History"])

    with tab1:
        products = get_recent_products(limit=15)
        if products:
            p_data = [
                {
                    "ID": p.id,
                    "Product Name": p.product_name or "—",
                    "Brand": p.brand or "—",
                    "Model Number": p.model_number or "—",
                    "Serial Number": p.serial_number or "—",
                    "Category": p.product_category or "—",
                    "Created At": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "—",
                }
                for p in products
            ]
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
        else:
            st.info("No products extracted yet. Go to **Document Upload & Extraction** to process your first invoice or manual!")

    with tab2:
        docs = get_recent_documents(limit=15)
        if docs:
            d_data = [
                {
                    "ID": d.id,
                    "File Name": d.file_name,
                    "Type": d.document_type or "—",
                    "Product ID": d.product_id or "—",
                    "Uploaded At": d.uploaded_at.strftime("%Y-%m-%d %H:%M") if d.uploaded_at else "—",
                }
                for d in docs
            ]
            st.dataframe(pd.DataFrame(d_data), use_container_width=True, hide_index=True)
        else:
            st.info("No documents uploaded yet.")


def page_upload_and_extract():
    st.markdown('<div class="main-header">📄 Document Upload & Extraction</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Upload product invoices, user manuals, warranty certificates, or label photos to extract product identity attributes.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a document to process",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Supported formats: PDF (native or scanned), PNG, JPG, JPEG",
    )

    if uploaded_file:
        file_ext = Path(uploaded_file.name).suffix.lower()
        file_size_kb = uploaded_file.size / 1024

        col_meta1, col_meta2, col_meta3 = st.columns(3)
        col_meta1.metric("File Name", uploaded_file.name)
        col_meta2.metric("File Format", file_ext.upper())
        col_meta3.metric("File Size", f"{file_size_kb:.1f} KB")

        st.markdown("---")

        if st.button("🚀 Process Document (OCR + Extraction)", type="primary", use_container_width=True):
            # Save uploaded file to a temporary file for PyMuPDF/pytesseract processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = Path(tmp_file.name)

            try:
                with st.spinner("Extracting text via PyMuPDF / Tesseract OCR..."):
                    extracted_text = extract_text(tmp_path)

                if not extracted_text or not extracted_text.strip():
                    st.warning("Document processing completed, but no readable text could be extracted from this document.")
                    return

                with st.spinner("Analyzing text & extracting product identity attributes..."):
                    product = extract_product_info(extracted_text)

                # Persist to database
                with st.spinner("Saving records to SQLite database..."):
                    doc, db_product = save_processed_document(
                        file_name=uploaded_file.name,
                        file_path=str(tmp_path),
                        document_type=file_ext,
                        extracted_text=extracted_text,
                        product_data=product,
                    )

                st.success("✅ Document processed and product information saved successfully!")

                # Display Results in Clean Cards
                st.subheader("Extracted Product Identity")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.text_input("Product Name", value=product.product_name or "Not Detected", disabled=True)
                    st.text_input("Brand", value=product.brand or "Not Detected", disabled=True)
                with c2:
                    st.text_input("Model Number", value=product.model_number or "Not Detected", disabled=True)
                    st.text_input("Serial Number", value=product.serial_number or "Not Detected", disabled=True)
                with c3:
                    st.text_input("Category", value=product.product_category or "Not Detected", disabled=True)
                    st.text_input("Database Record ID", value=str(db_product.id if db_product else "None"), disabled=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Expanders for Raw Text and JSON Details
                with st.expander("📄 View Extracted Raw Document Text (OCR Preview)"):
                    st.text_area("Extracted Text", value=extracted_text, height=260, disabled=True)

                with st.expander("🔍 View Structured JSON Data"):
                    st.json(product.model_dump())

            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
            finally:
                # Cleanup temp file
                if tmp_path.exists():
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass


def page_recall_preview():
    st.markdown('<div class="main-header">🔍 CPSC Recall Intelligence Database</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Official United States Consumer Product Safety Commission (CPSC) recall repository.</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "ℹ️ **Ticket 1 Scope Notice:** Automated Recall Matching (RapidFuzz cross-document matching & Evidence RAG) "
        "is scheduled for subsequent tickets. This interface provides verified access and search capability into "
        "the 562 official CPSC appliance and electronics recall records imported into ProofGuard.",
        icon="ℹ️",
    )

    search_query = st.text_input(
        "🔎 Search recalls by keyword (e.g. Samsung, Washing Machine, Fire, LG, Refrigerator):",
        placeholder="Type brand, model, product name, or hazard...",
    )

    limit = st.slider("Max records to display:", min_value=10, max_value=200, value=50, step=10)

    recalls = get_available_recalls(limit=limit, search_query=search_query)

    st.write(f"Showing **{len(recalls)}** recall records:")

    if recalls:
        table_rows = []
        for r in recalls:
            models_str = ", ".join(r.model_numbers) if r.model_numbers else "—"
            table_rows.append(
                {
                    "Recall ID": r.external_recall_id,
                    "Product Name": r.product_name or "—",
                    "Manufacturer": r.manufacturer or "—",
                    "Affected Models": models_str,
                    "Recall Date": r.recall_date or "—",
                    "Hazard Description": (r.hazard_description[:120] + "...") if r.hazard_description and len(r.hazard_description) > 120 else (r.hazard_description or "—"),
                    "Remedy": (r.remedy[:100] + "...") if r.remedy and len(r.remedy) > 100 else (r.remedy or "—"),
                    "Source URL": r.source_url or "—",
                }
            )

        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Detailed Record Inspection")
        selected_id = st.selectbox("Select a Recall ID to view full safety details:", [r.external_recall_id for r in recalls])
        selected_recall = next((r for r in recalls if r.external_recall_id == selected_id), None)

        if selected_recall:
            st.markdown(f"### {selected_recall.product_name or 'Product Recall'}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**External ID:** `{selected_recall.external_recall_id}`")
                st.markdown(f"**Manufacturer:** {selected_recall.manufacturer or 'N/A'}")
                st.markdown(f"**Recall Date:** {selected_recall.recall_date or 'N/A'}")
                st.markdown(f"**Models:** {', '.join(selected_recall.model_numbers) if selected_recall.model_numbers else 'None listed'}")
            with col_b:
                st.markdown(f"**Official URL:** [{selected_recall.source_url}]({selected_recall.source_url})" if selected_recall.source_url else "**Official URL:** None")

            st.markdown("**Hazard Description:**")
            st.warning(selected_recall.hazard_description or "No hazard details available.")

            st.markdown("**Corrective Remedy:**")
            st.success(selected_recall.remedy or "No remedy specified.")
    else:
        st.warning("No recall records matched your search query.")


def page_about():
    st.markdown('<div class="main-header">ℹ️ ProofGuard Architecture & Team Allocation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">System Foundation, Original Responsibilities, and Technical Specifications</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### Project Overview
        **ProofGuard** is an evidence-based product recall intelligence platform.
        Ticket 1 establishes the verified data and system foundation, connecting document processing,
        entity extraction, database storage, and official regulatory recall datasets.

        ### Team Task Allocation & Deliverables
        | Member | Assigned Responsibility | Deliverable Completed |
        |---|---|---|
        | **Aswin (Lead)** | Architecture, DB Schema, Project Foundation | SQLite schema, SQLAlchemy models, Pydantic schemas, database initialization, document service |
        | **Abhinav** | PDF Extraction & OCR Fallback | `app/ocr/document_processor.py`, PyMuPDF + Tesseract integration, 11 tests |
        | **Ashfaq** | CPSC Recall Data Collection | `app/recalls/cpsc_collector.py`, 562 verified records, import pipeline, 6 tests |
        | **Arun** | Product Information Extraction | `app/extraction/product_extractor.py`, regex + spaCy NER, 54 tests |
        | **Vignesh** | Streamlit Upload & Dashboard UI | `ui/app.py`, Document upload, OCR preview, Extraction cards, CPSC browser, Metrics dashboard |

        ### Processing Pipeline
        ```
        User Document (PDF / Image)
                    │
                    ▼
        [ Document Processor & OCR (Abhinav) ]
          - Digital PDF text extraction (PyMuPDF)
          - Scanned fallback to 200 DPI rasterization + Tesseract OCR
                    │
                    ▼
        [ Product Extractor (Arun / Ashfaq) ]
          - Text normalization & noise cleaning
          - spaCy NER + Brand Gazetteer (Samsung, LG, Whirlpool, etc.)
          - Model & Serial regex with disambiguation
          - Category Classification (Home / Kitchen / Electronics)
                    │
                    ▼
        [ SQLite Database Persistence (Aswin) ]
          - Documents table (extracted text, metadata)
          - Products table (structured attributes)
                    │
                    ▼
        [ Streamlit Interface (Vignesh) ]
          - Upload & real-time OCR/Extraction preview
          - CPSC Recall repository lookup
          - Operational metrics dashboard
        ```
        """
    )


def main():
    page = render_sidebar()
    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📄 Document Upload & Extraction":
        page_upload_and_extract()
    elif page == "🔍 CPSC Recall Intelligence":
        page_recall_preview()
    elif page == "ℹ️ Architecture & About":
        page_about()


if __name__ == "__main__":
    main()
