# utils.py
import base64
import io
import pdf2image
import streamlit as st
import pdfkit # Import pdfkit
import markdown # Import markdown
from tempfile import NamedTemporaryFile # For temporary PDF file creation
import os # For file cleanup
import datetime

from config import POPPLER_PATH, WKHTMLTOPDF_PATH # Import WKHTMLTOPDF_PATH from config

def pdf_to_base64_images(uploaded_file, pages_to_process=1):
    """
    Converts PDF pages to JPEG images and then Base64 encodes them for multimodal input.
    """
    if uploaded_file is None:
        st.error("No file provided for PDF to image conversion.")
        return []

    images_parts = []
    try:
        pdf_bytes = uploaded_file.read()

        if POPPLER_PATH:
            images = pdf2image.convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)
        else:
            images = pdf2image.convert_from_bytes(pdf_bytes)

        for i, image in enumerate(images):
            if i >= pages_to_process:
                break

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', optimize=True, quality=85)
            img_byte_arr = img_byte_arr.getvalue() # Get bytes

            encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')

            images_parts.append(
                {
                    "mime_type": "image/jpeg",
                    "data": encoded_image
                }
            )
        st.success(f"Successfully processed {len(images_parts)} page(s) from the PDF.")
    except Exception as e:
        st.error(f"Error converting PDF to images: {str(e)}. Please ensure Poppler is installed and configured correctly (especially for Windows users, check POPPLER_PATH).")
        return []

    return images_parts

def sanitize_filename(name):
    """Converts a string to a safe filename."""
    return "".join(c if c.isalnum() or c in [' ', '_', '-'] else "_" for c in name).strip("_")

def generate_pdf_from_markdown(markdown_content, title="Report", footer_text="ResumeFlow AI", filename="report.pdf"):
    """
    Generates a PDF from markdown content using wkhtmltopdf.
    """
    html_content = markdown.markdown(markdown_content)

    # Basic HTML template for the PDF
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 40px;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                font-size: 2em;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }}
            h2 {{
                font-size: 1.5em;
                border-bottom: 2px solid #ccc;
                padding-bottom: 8px;
                margin-top: 30px;
                color: #34495e;
            }}
            h3 {{
                font-size: 1.2em;
                color: #555;
                margin-top: 20px;
            }}
            ul {{
                list-style-type: disc;
                margin-left: 25px;
                padding-left: 0;
            }}
            ol {{
                list-style-type: decimal;
                margin-left: 25px;
                padding-left: 0;
            }}
            li {{
                margin-bottom: 8px;
            }}
            strong {{
                font-weight: bold;
                color: #2c3e50;
            }}
            em {{
                font-style: italic;
            }}
            p {{
                margin-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                font-size: 0.8em;
                color: #777;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: #fff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            {html_content}
            <div class="footer">
                <p>{footer_text}</p>
                <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        config = None
        if WKHTMLTOPDF_PATH:
            config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            if config:
                pdfkit.from_string(full_html, tmp_pdf.name, configuration=config)
            else:
                pdfkit.from_string(full_html, tmp_pdf.name)
            tmp_pdf.seek(0)
            pdf_data = tmp_pdf.read()
        os.unlink(tmp_pdf.name) # Clean up the temporary PDF file
        return pdf_data
    except Exception as e:
        st.error(f"Error generating PDF: {e}. Please ensure 'wkhtmltopdf' is installed and in your system's PATH, or configure WKHTMLTOPDF_PATH in config.py.")
        return None