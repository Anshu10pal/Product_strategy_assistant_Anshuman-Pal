"""
Document Parser Utility
Parses uploaded files into plain text for ingestion.
Supports: CSV, TXT, JSON, PDF
"""

import io
import json
import pandas as pd
from typing import Tuple


def parse_csv(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Parse CSV into a readable text summary."""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        lines = [f"File: {filename}", f"Rows: {len(df)}, Columns: {len(df.columns)}"]
        lines.append(f"Columns: {', '.join(df.columns.tolist())}")
        lines.append("\nSample Data (first 20 rows):")
        lines.append(df.head(20).to_string(index=False))

        # Basic numeric stats
        numeric_cols = df.select_dtypes(include="number")
        if not numeric_cols.empty:
            lines.append("\nNumeric Summary:")
            lines.append(numeric_cols.describe().to_string())

        # Categorical columns value counts
        cat_cols = df.select_dtypes(include="object")
        for col in cat_cols.columns[:5]:  # limit to 5
            top = df[col].value_counts().head(5)
            lines.append(f"\nTop values in '{col}':\n{top.to_string()}")

        return "\n".join(lines), "sales_data"
    except Exception as e:
        return f"Error parsing CSV: {e}", "unknown"


def parse_txt(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Parse plain text file."""
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
        return f"File: {filename}\n\n{text}", "text_document"
    except Exception as e:
        return f"Error parsing TXT: {e}", "unknown"


def parse_json(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Parse JSON file into readable text."""
    try:
        data = json.loads(file_bytes.decode("utf-8"))
        text = json.dumps(data, indent=2)
        return f"File: {filename}\n\n{text}", "json_document"
    except Exception as e:
        return f"Error parsing JSON: {e}", "unknown"


def parse_pdf(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Parse PDF file using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n\n".join(text_parts)
        return f"File: {filename}\n\n{full_text}", "pdf_document"
    except Exception as e:
        return f"Error parsing PDF: {e}", "unknown"


def parse_file(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Route file to the correct parser based on extension.
    Returns (content_text, doc_type)
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "txt"

    if ext == "csv":
        return parse_csv(file_bytes, filename)
    elif ext in ("txt", "md"):
        return parse_txt(file_bytes, filename)
    elif ext == "json":
        return parse_json(file_bytes, filename)
    elif ext == "pdf":
        return parse_pdf(file_bytes, filename)
    else:
        # Try plain text as fallback
        return parse_txt(file_bytes, filename)
