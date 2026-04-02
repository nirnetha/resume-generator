import os
from flask import Flask, render_template, request, make_response, url_for

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    pdfkit = None
    PDFKIT_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'replace-with-a-strong-secret')

# Configure pdfkit with explicit wkhtmltopdf path
# Default Windows path: C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
# Can be overridden with environment variable WKHTMLTOPDF_PATH
WKHTMLTOPDF_PATH = (
    os.environ.get('WKHTMLTOPDF_PATH') or
    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
)

PDFKIT_CONFIG = None
if PDFKIT_AVAILABLE:
    try:
        # Create pdfkit configuration with the specified wkhtmltopdf path
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    except Exception as e:
        # Configuration created but path may not exist yet
        print(f"Warning: pdfkit configuration created, but wkhtmltopdf may not be at: {WKHTMLTOPDF_PATH}")
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


def parse_form_data(form):
    """Map input form into structured resume data."""
    skills = [s.strip() for s in form.getlist('skills[]') if s.strip()]

    projects = []
    for title, desc, link in zip(
        form.getlist('project_titles[]'),
        form.getlist('project_descs[]'),
        form.getlist('project_links[]'),
    ):
        if title.strip() or desc.strip() or link.strip():
            projects.append({
                'title': title.strip(),
                'description': desc.strip(),
                'link': link.strip(),
            })

    experience = []
    for title, company, period, description in zip(
        form.getlist('exp_titles[]'),
        form.getlist('exp_companies[]'),
        form.getlist('exp_periods[]'),
        form.getlist('exp_duties[]'),
    ):
        if title.strip() or company.strip() or period.strip() or description.strip():
            experience.append({
                'title': title.strip(),
                'company': company.strip(),
                'period': period.strip(),
                'description': description.strip(),
            })

    certifications = [c.strip() for c in form.getlist('certifications[]') if c.strip()]
    extras = [e.strip() for e in form.getlist('extras[]') if e.strip()]

    return {
        'name': form.get('name', '').strip(),
        'email': form.get('email', '').strip(),
        'phone': form.get('phone', '').strip(),
        'location': form.get('location', '').strip(),
        'linkedin': form.get('linkedin', '').strip(),
        'github': form.get('github', '').strip(),
        'job_title': form.get('job_title', '').strip(),
        'summary': form.get('summary', '').strip(),
        'degree': form.get('degree', '').strip(),
        'institute': form.get('institute', '').strip(),
        'grad_year': form.get('grad_year', '').strip(),
        'skills': skills,
        'projects': projects,
        'experience': experience,
        'certifications': certifications,
        'extra_curricular': extras,
        'achievements': [a.strip() for a in form.getlist('achievements[]') if a.strip()],
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        info = parse_form_data(request.form)

        # Render clean HTML resume only (plain-text builder no longer used)
        return render_template('resume.html', info=info)

    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    """Generate and download resume as PDF."""
    if not PDFKIT_AVAILABLE:
        return (
            "<h2>PDF Generation Not Available</h2>"
            "<p>The pdfkit Python package is not installed.</p>"
            "<p>Install it with: <code>pip install pdfkit</code></p>"
            "<p><a href='/'>← Back to Form</a></p>"
        ), 500

    info = parse_form_data(request.form)
    resume_html = render_template('resume_pdf.html', info=info)

    try:
        # Generate PDF from HTML using pdfkit with configured wkhtmltopdf path
        pdf = pdfkit.from_string(
            resume_html,
            False,
            configuration=PDFKIT_CONFIG,
            options={
                'page-size': 'A4',
                'margin-top': '10mm',
                'margin-bottom': '10mm',
                'margin-left': '12mm',
                'margin-right': '12mm',
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
            },
        )

        # Prepare response with PDF file download
        filename_base = info.get('name', 'resume').strip().replace(' ', '_') or 'resume'
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename_base}_resume.pdf"'
        return response

    except OSError as e:
        # wkhtmltopdf executable not found at configured path
        error_msg = (
            "<h2>PDF Generation Failed</h2>"
            "<p><strong>wkhtmltopdf not found at:</strong></p>"
            f"<p><code>{WKHTMLTOPDF_PATH}</code></p>"
            "<p><strong>Installation Instructions:</strong></p>"
            "<ul>"
            f"<li><strong>Windows:</strong> Download from <a href='https://wkhtmltopdf.org/download.html' target='_blank'>wkhtmltopdf.org</a> "
            f"and install to <code>C:\\Program Files\\wkhtmltopdf</code></li>"
            "<li><strong>Or set environment variable:</strong> <code>set WKHTMLTOPDF_PATH=C:\\your\\path\\wkhtmltopdf.exe</code></li>"
            "<li><strong>Mac:</strong> <code>brew install wkhtmltopdf</code></li>"
            "<li><strong>Linux:</strong> <code>sudo apt-get install wkhtmltopdf</code></li>"
            "</ul>"
            "<p>After installation, restart this app and try downloading again.</p>"
            "<p><a href='/'>← Back to Form</a></p>"
        )
        return error_msg, 500

    except Exception as e:
        # Catch all other errors
        error_msg = (
            "<h2>PDF Generation Error</h2>"
            f"<p><strong>Error:</strong> {str(e)}</p>"
            "<p>Please check that wkhtmltopdf is properly installed.</p>"
            "<p><a href='/'>← Back to Form</a></p>"
        )
        return error_msg, 500


if __name__ == '__main__':
    app.run(debug=True)