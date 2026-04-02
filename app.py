import os
from flask import Flask, render_template, request, make_response, url_for

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    pdfkit = None
    PDFKIT_AVAILABLE = False

from resume_generator import build_resume

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'replace-with-a-strong-secret')

# Setup pdfkit configuration with optional WKHTMLTOPDF path set via env var
WKHTMLTOPDF_PATH = os.environ.get('WKHTMLTOPDF_PATH')
PDFKIT_CONFIG = None
if PDFKIT_AVAILABLE and WKHTMLTOPDF_PATH:
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

        # Keep old logic tied, but not shown to users; builds hidden text if needed.
        build_resume(info)

        return render_template('resume.html', info=info)

    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    if not PDFKIT_AVAILABLE:
        return "PDF generation requires the pdfkit package. Install it with: pip install pdfkit", 500

    info = parse_form_data(request.form)

    resume_html = render_template('resume_pdf.html', info=info)

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

    filename_base = info.get('name', 'resume').strip().replace(' ', '_') or 'resume'
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename_base}_resume.pdf"'
    return response


if __name__ == '__main__':
    app.run(debug=True)