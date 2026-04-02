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

# Render / Linux friendly wkhtmltopdf configuration.
# Don't force Windows-specific path. Use env var if available.
PDFKIT_CONFIG = None
if PDFKIT_AVAILABLE:
    wkhtmltopdf_path = os.environ.get('WKHTMLTOPDF_PATH')
    if wkhtmltopdf_path:
        try:
            PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        except Exception as e:
            print(f"Warning: wkhtmltopdf path from WKHTMLTOPDF_PATH not valid: {wkhtmltopdf_path}")
            PDFKIT_CONFIG = None
    else:
        # Let pdfkit attempt default Linux path resolution
        try:
            PDFKIT_CONFIG = pdfkit.configuration()
        except Exception as e:
            print("Warning: wkhtmltopdf not configured by env var and not found in PATH.")
            PDFKIT_CONFIG = None


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
        # wkhtmltopdf not available or not executable
        error_msg = (
            "<h2>PDF Generation Failed</h2>"
            "<p>wkhtmltopdf executable could not be found or started.</p>"
            "<p>Check that wkhtmltopdf is installed and available in PATH, or set WKHTMLTOPDF_PATH environment variable.</p>"
            "<p><strong>Install instructions (Linux/Render):</strong></p>"
            "<ul>"
            "<li>Ubuntu/Debian: <code>sudo apt-get install wkhtmltopdf</code></li>"
            "<li>Mac: <code>brew install wkhtmltopdf</code></li>"
            "<li>Render: add wkhtmltopdf install step in build command or container</li>"
            "</ul>"
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
    # For deployment on Render (or similar), listen on all interfaces and port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)