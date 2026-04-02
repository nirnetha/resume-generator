import os
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'replace-with-a-strong-secret')


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


if __name__ == '__main__':
    # For deployment on Render (or similar), listen on all interfaces and port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)