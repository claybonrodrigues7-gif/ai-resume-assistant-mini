import sys

from resume_assistant import ResumeInput, build_resume_sections, load_resume_from_file, save_report


def prompt_for_resume_data() -> ResumeInput:
    print("Enter your resume details:\n")

    qualification = input("Qualification: ").strip()
    technical_skills = input("Technical skills (comma-separated): ").strip()
    experience = input("Experience: ").strip()
    projects = input("Project names (press Enter to skip): ").strip()

    data = {
        "qualification": qualification,
        "technical_skills": technical_skills,
        "experience": experience,
        "projects": [{"name": projects, "description": "", "tech_stack": ""}] if projects else [],
        "career_objective": "",
    }

    return ResumeInput.from_dict(data)


def main():
    if len(sys.argv) > 1:
        resume = load_resume_from_file(sys.argv[1])
    else:
        resume = prompt_for_resume_data()

    sections = build_resume_sections(resume)

    print("\nGenerated Resume Sections\n")
    print("1. Career Objective")
    print(sections["career_objective"])
    print("\n2. Technical Skills")
    print(sections["technical_skills"])
    print("\n3. Project Descriptions")
    print(sections["project_descriptions"])

    save_report("resume_output.txt", sections)
    print("\nSaved to resume_output.txt")


if __name__ == "__main__":
    main()

