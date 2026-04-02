def get_user_info():
    print("\n" + "=" * 50)
    print("      Welcome to the Resume Generator!")
    print("=" * 50)
    print("Fill in the details below. Press Enter to continue.\n")

    name       = input("Full Name:                  ")
    email      = input("Email Address:              ")
    phone      = input("Phone Number:               ")
    location   = input("City, State (e.g. Mumbai):  ")
    linkedin   = input("LinkedIn/Portfolio URL:     ")
    projects   = input("Enter your projects:        ")

    print("\n--- Job Target ---")
    job_title  = input("Job Title you are applying for: ")
    summary    = input("Write a short summary about yourself (1-2 lines): ")

    print("\n--- Skills ---")
    skills_raw = input("List your skills separated by commas\n  e.g. Python, Excel, Communication: ")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    print("\n--- Work Experience ---")
    print("Enter up to 2 jobs. Leave blank to skip.\n")
    jobs = []
    for i in range(1, 3):
        print(f"  Job {i}:")
        title   = input("    Job Title (or press Enter to skip): ")
        if not title:
            break
        company = input("    Company Name: ")
        period  = input("    Period (e.g. Jan 2022 - Mar 2024): ")
        duties  = input("    Key responsibilities (one line): ")
        jobs.append({
            "title": title,
            "company": company,
            "period": period,
            "duties": duties
        })

    print("\n--- Education ---")
    degree    = input("Degree/Qualification: ")
    institute = input("College/University:   ")
    grad_year = input("Year of Graduation:   ")

    print("\n--- Achievements (optional) ---")
    achievements_raw = input("List achievements separated by commas (or press Enter to skip): ")
    achievements = [a.strip() for a in achievements_raw.split(",") if a.strip()]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "projects": projects,   # ✅ ADDED
        "job_title": job_title,
        "summary": summary,
        "skills": skills,
        "jobs": jobs,
        "degree": degree,
        "institute": institute,
        "grad_year": grad_year,
        "achievements": achievements,
    }


def build_resume(info):

    def section(title):
        return f"\n{title}\n" + "-" * 40

    resume = ""

    # --- Header ---
    resume += "=" * 50 + "\n"
    resume += info["name"].upper().center(50) + "\n"
    resume += "=" * 50 + "\n"

    contact_parts = []
    if info["email"]:    contact_parts.append(info["email"])
    if info["phone"]:    contact_parts.append(info["phone"])
    if info["location"]: contact_parts.append(info["location"])
    if info["linkedin"]: contact_parts.append(info["linkedin"])
    resume += "  |  ".join(contact_parts) + "\n"

    # --- Objective ---
    if info["summary"]:
        resume += section("OBJECTIVE")
        resume += f"\n{info['summary']}\n"

    # --- Skills ---
    if info["skills"]:
        resume += section("SKILLS")
        row = []
        for i, skill in enumerate(info["skills"], 1):
            row.append(f"  * {skill:<20}")
            if i % 3 == 0:
                resume += "\n" + "".join(row)
                row = []
        if row:
            resume += "\n" + "".join(row)
        resume += "\n"

    # --- Work Experience ---
    if info["jobs"]:
        resume += section("WORK EXPERIENCE")
        for job in info["jobs"]:
            resume += f"\n{job['title']} -- {job['company']}\n"
            resume += f"  {job['period']}\n"
            resume += f"  * {job['duties']}\n"

    # --- Education ---
    if info["degree"]:
        resume += section("EDUCATION")
        resume += f"\n{info['degree']}\n"
        resume += f"  {info['institute']}"
        if info["grad_year"]:
            resume += f",  {info['grad_year']}"
        resume += "\n"

    # --- Projects ---  ✅ NEW SECTION
    if info["projects"]:
        resume += section("PROJECTS")
        resume += f"\n  * {info['projects']}\n"

    # --- Achievements ---
    if info["achievements"]:
        resume += section("ACHIEVEMENTS")
        for item in info["achievements"]:
            resume += f"\n  * {item}"
        resume += "\n"

    resume += "\n" + "=" * 50 + "\n"
    return resume


def save_resume(resume_text, name):
    filename = name.strip().replace(" ", "_") + "_resume.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(resume_text)
    return filename


def main():
    info   = get_user_info()
    resume = build_resume(info)

    print("\n" + "=" * 50)
    print("           YOUR RESUME PREVIEW")
    print("=" * 50)
    print(resume)

    choice = input("Save this resume to a .txt file? (yes/no): ").strip().lower()
    if choice == "yes":
        filename = save_resume(resume, info["name"])
        print(f"\nSaved as: {filename}")
    else:
        print("\nDone! Copy the text above if you need it.")


if __name__ == "__main__":
    main()