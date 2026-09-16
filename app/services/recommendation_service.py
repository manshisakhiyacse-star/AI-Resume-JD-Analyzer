from typing import List

class RecommendationService:
    @staticmethod
    def format_skill_display(skill: str) -> str:
        """
        Formats a canonical lowercase skill name for professional display (e.g., aws -> AWS, python -> Python).
        """
        abbreviations = {
            "aws": "AWS",
            "gcp": "GCP",
            "nlp": "NLP",
            "api": "API",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS",
            "js": "JS",
            "ts": "TS",
            "db": "DB",
            "txt": "TXT",
            "rest api": "REST API",
            "nextjs": "Next.js",
            "nodejs": "Node.js",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
            "fastapi": "FastAPI",
            "elasticsearch": "Elasticsearch",
            "github actions": "GitHub Actions"
        }
        
        skill_lower = skill.lower().strip()
        if skill_lower in abbreviations:
            return abbreviations[skill_lower]
            
        # Title case others (e.g., spring boot -> Spring Boot)
        return skill_lower.title()

    @classmethod
    def generate_recommendations(cls, missing_skills: List[str]) -> List[str]:
        """
        Generates actionable, non-falsifying recommendations based on detected skill gaps.
        Grounded strictly in the missing skills list.
        """
        if not missing_skills:
            return ["Excellent! Your resume matches all key technical skills identified in the job description."]
            
        recommendations = []
        
        # Categorized templates based on skill keywords
        devops_keywords = {"docker", "kubernetes", "jenkins", "terraform", "ansible", "k8s"}
        db_keywords = {"postgresql", "mysql", "mongodb", "redis", "sqlite", "cassandra", "elasticsearch", "sql"}
        cloud_keywords = {"amazon web services", "google cloud platform", "microsoft azure", "aws", "gcp", "azure"}
        lang_keywords = {"python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "ruby", "scala", "kotlin", "swift"}
        framework_keywords = {"fastapi", "spring boot", "react", "django", "flask", "angular", "vue", "nextjs", "pytorch", "tensorflow", "keras", "express"}

        for skill in missing_skills:
            skill_lower = skill.lower().strip()
            display_name = cls.format_skill_display(skill_lower)
            
            if skill_lower in cloud_keywords:
                recommendations.append(
                    f"Highlight your cloud infrastructure, deployment, or architecture experience using {display_name} if applicable."
                )
            elif skill_lower in devops_keywords:
                recommendations.append(
                    f"Add details about your containerization, CI/CD orchestration, or infrastructure-as-code workflows using {display_name} if you have worked with it."
                )
            elif skill_lower in db_keywords:
                recommendations.append(
                    f"Mention database modeling, optimization, or queries involving {display_name} if you have hands-on experience."
                )
            elif skill_lower in lang_keywords:
                recommendations.append(
                    f"Incorporate software development projects or systems you have built using {display_name} if applicable."
                )
            elif skill_lower in framework_keywords:
                recommendations.append(
                    f"Highlight web application development or machine learning model development using the {display_name} framework if you have experience."
                )
            else:
                recommendations.append(
                    f"Consider highlighting projects or work history demonstrating your experience with {display_name} if you have worked with it."
                )
                
        return recommendations
