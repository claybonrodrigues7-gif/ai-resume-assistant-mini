import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class ResumeInput:
    qualification: str = ""
    technical_skills: List[str] = field(default_factory=list)
    projects: List[Dict[str, str]] = field(default_factory=list)
    experience: str = ""
    career_objective: str = ""

    @staticmethod
    def normalize_skill_list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [s.strip() for s in re.split(r"[,\n;]+", value) if s.strip()]
        return []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResumeInput":
        projects = []
        raw_projects = data.get("projects", [])

        if isinstance(raw_projects, list):
            for item in raw_projects:
                if isinstance(item, dict):
                    projects.append(
                        {
                            "name": str(item.get("name", "Project")).strip(),
                            "description": str(item.get("description", "")).strip(),
                            "tech_stack": str(item.get("tech_stack", "")).strip(),
                        }
                    )
                elif isinstance(item, str):
                    projects.append({"name": item.strip(), "description": "", "tech_stack": ""})

        return cls(
            qualification=str(data.get("qualification", "")).strip(),
            technical_skills=cls.normalize_skill_list(data.get("technical_skills", [])),
            projects=projects,
            experience=str(data.get("experience", "")).strip(),
            career_objective=str(data.get("career_objective", "")).strip(),
        )


def infer_role(skills: List[str]) -> str:
    skill_text = " ".join(skill.lower() for skill in skills)

    if any(word in skill_text for word in ["machine learning", "deep learning", "ai", "nlp", "computer vision"]):
        return "Machine Learning Engineer"
    if any(word in skill_text for word in ["power bi", "sql", "data analysis", "tableau"]):
        return "Data Analyst"
    if any(word in skill_text for word in ["react", "django", "flask", "fastapi", "web", "javascript"]):
        return "Full Stack Developer"
    if any(word in skill_text for word in ["docker", "aws", "azure", "kubernetes", "cloud"]):
        return "Cloud Engineer"
    if any(word in skill_text for word in ["cyber", "security", "ethical hacking"]):
        return "Cybersecurity Analyst"
    return "Software Developer"


def extract_years(experience: str) -> str:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)", experience, flags=re.IGNORECASE)
    if match:
        return match.group(0)
    return "relevant professional experience"


def generate_career_objective(data: ResumeInput) -> str:
    if data.career_objective.strip():
        return data.career_objective.strip()

    role = infer_role(data.technical_skills)
    years = extract_years(data.experience)
    qualification = data.qualification if data.qualification else "graduate with a strong foundation in technology"

    return (
        f"Driven {role} with {qualification} and {years} of hands-on experience in software development "
        f"and problem solving. Eager to contribute strong technical skills, analytical thinking, and "
        f"project execution abilities to build impactful solutions that solve real-world challenges while "
        f"continuing to learn, innovate, and grow in a dynamic professional environment."
    )


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    languages = []
    frameworks = []
    databases = []
    cloud_devops = []
    tools = []
    ai_ml = []

    for skill in skills:
        key = skill.lower().strip()
        if not key:
            continue

        if any(word in key for word in ["python", "java", "c++", "c#", "javascript", "typescript", "sql", "html", "css", "bash"]):
            languages.append(skill)
        elif any(word in key for word in ["flask", "django", "fastapi", "react", "node", "express", "spring", "pandas", "numpy", "scikit", "tensorflow", "keras", "pytorch"]):
            frameworks.append(skill)
        elif any(word in key for word in ["mysql", "postgres", "mongodb", "sqlite", "oracle", "db"]):
            databases.append(skill)
        elif any(word in key for word in ["aws", "azure", "gcp", "docker", "kubernetes", "devops", "ci", "cd"]):
            cloud_devops.append(skill)
        elif any(word in key for word in ["git", "github", "jira", "linux", "postman", "figma", "vscode"]):
            tools.append(skill)
        elif any(word in key for word in ["machine learning", "deep learning", "nlp", "ai", "computer vision", "ml"]):
            ai_ml.append(skill)
        else:
            frameworks.append(skill)

    return {
        "Programming Languages": sorted(set(languages)),
        "Frameworks & Libraries": sorted(set(frameworks)),
        "Databases": sorted(set(databases)),
        "Cloud & DevOps": sorted(set(cloud_devops)),
        "AI / ML": sorted(set(ai_ml)),
        "Tools & Platforms": sorted(set(tools)),
    }


def generate_technical_skills_section(data: ResumeInput) -> str:
    categorized = categorize_skills(data.technical_skills)
    lines = ["Technical Skills", "-"]

    for category, items in categorized.items():
        if items:
            lines.append(f"{category}: {', '.join(items)}")

    if not any(categorized.values()):
        lines.append("No technical skills provided.")

    return "\n".join(lines)


def generate_project_descriptions(data: ResumeInput) -> str:
    if not data.projects:
        return "Project Descriptions\n\nNo projects provided."

    output = ["Project Descriptions", ""]

    for index, project in enumerate(data.projects, start=1):
        name = project.get("name", f"Project {index}")
        description = project.get("description", "").strip()
        tech_stack = project.get("tech_stack", "").strip()

        if not description:
            description = (
                "Developed a technology-driven solution focused on solving a real-world problem using "
                "modern tools and best engineering practices. The project emphasizes efficiency, user "
                "experience, and reliable performance while applying core concepts in software development "
                "and system design."
            )

        project_text = f"{index}. {name}\n   - {description}"
        if tech_stack:
            project_text += f"\n   - Tech Stack: {tech_stack}"
        output.append(project_text)

    return "\n".join(output)


def generate_ai_response(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return ""

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Write concise, polished content."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def build_resume_sections(data: ResumeInput) -> Dict[str, str]:
    objective = generate_career_objective(data)
    skills = generate_technical_skills_section(data)
    projects = generate_project_descriptions(data)

    return {
        "career_objective": objective,
        "technical_skills": skills,
        "project_descriptions": projects,
    }


def save_report(filename: str, sections: Dict[str, str]) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write("AI Resume Assistant Output\n")
        file.write("=" * 30 + "\n\n")
        file.write("1. Career Objective\n")
        file.write(sections["career_objective"] + "\n\n")
        file.write("2. Technical Skills\n")
        file.write(sections["technical_skills"] + "\n\n")
        file.write("3. Project Descriptions\n")
        file.write(sections["project_descriptions"] + "\n")


def load_resume_from_file(path: str) -> ResumeInput:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return ResumeInput.from_dict(data)


if __name__ == "__main__":
    sample = {
        "qualification": "B.Tech in Computer Science",
        "technical_skills": ["Python", "Machine Learning", "NLP", "SQL", "Flask", "FastAPI", "Docker", "Git", "AWS", "JavaScript"],
        "experience": "2 years of software engineering experience",
        "career_objective": "",
        "projects": [
            {
                "name": "AI Resume Assistant",
                "description": "Built a Python application that converts user profile data into polished resume sections like career objective, technical skills, and project descriptions.",
                "tech_stack": "Python, OpenAI, JSON, Git",
            },
            {
                "name": "Sentiment Analysis Dashboard",
                "description": "Developed a dashboard to analyze customer sentiment from product reviews and visualize trends using ML models.",
                "tech_stack": "Python, Pandas, Scikit-learn, Flask, SQL",
            },
        ],
    }
    sections = build_resume_sections(ResumeInput.from_dict(sample))
    print(sections["career_objective"])
    print("\n" + sections["technical_skills"])
    print("\n" + sections["project_descriptions"])


