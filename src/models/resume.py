"""
Resume Model
Represents a user's resume with extracted information
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from .skill import Skill


class FileType(Enum):
    """Enum for supported resume file types"""
    PDF = "PDF"
    IMAGE = "IMAGE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Resume:
    """
    Represents a user's resume with extracted information.
    
    Attributes:
        filename: Original file name
        file_type: Type of file (PDF or IMAGE)
        extracted_text: Full text extracted from resume
        skills: List of identified skills
        user_name: Extracted user name
        email: Extracted email address
        phone: Extracted phone number
    """
    
    filename: str
    file_type: FileType = FileType.UNKNOWN
    extracted_text: str = ""
    skills: List[Skill] = field(default_factory=list)
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @property
    def skill_count(self) -> int:
        """Returns the total number of skills identified"""
        return len(self.skills)
    
    @property
    def technical_skills(self) -> List[Skill]:
        """Returns only technical skills"""
        return [skill for skill in self.skills if skill.is_technical]
    
    @property
    def soft_skills(self) -> List[Skill]:
        """Returns only soft skills"""
        return [skill for skill in self.skills if not skill.is_technical]
    
    def add_skill(self, skill: Skill) -> None:
        """
        Add a skill to the resume. If skill already exists, increment frequency.
        
        Args:
            skill: Skill object to add
        """
        # Check if skill already exists
        for existing_skill in self.skills:
            if existing_skill.matches(skill):
                existing_skill.increment_frequency()
                return
        
        # Add new skill
        self.skills.append(skill)
    
    def has_skill(self, skill_name: str) -> bool:
        """
        Check if resume contains a specific skill.
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            True if skill exists, False otherwise
        """
        return any(skill.matches_name(skill_name) for skill in self.skills)
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Retrieve a specific skill by name.
        
        Args:
            skill_name: Name of the skill to retrieve
            
        Returns:
            Skill object if found, None otherwise
        """
        for skill in self.skills:
            if skill.matches_name(skill_name):
                return skill
        return None
    
    def get_skills_as_string(self) -> str:
        """
        Get comma-separated list of skill names.
        
        Returns:
            String like "Python, Java, SQL"
        """
        return ", ".join(skill.name for skill in self.skills)
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """
        Get all skills in a specific category.
        
        Args:
            category: Category name (e.g., "Programming Language")
            
        Returns:
            List of skills in that category
        """
        return [skill for skill in self.skills 
                if skill.category.lower() == category.lower()]
    
    def clear_skills(self) -> None:
        """Remove all skills from resume"""
        self.skills.clear()
    
    def get_summary(self) -> str:
        """
        Get a summary of the resume.
        
        Returns:
            Formatted summary string
        """
        return (f"Resume: {self.filename}\n"
                f"Type: {self.file_type.value}\n"
                f"Name: {self.user_name or 'Not extracted'}\n"
                f"Email: {self.email or 'Not extracted'}\n"
                f"Phone: {self.phone or 'Not extracted'}\n"
                f"Skills Found: {self.skill_count}\n"
                f"Technical Skills: {len(self.technical_skills)}\n"
                f"Soft Skills: {len(self.soft_skills)}")
    
    def to_dict(self) -> dict:
        """
        Convert resume to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of resume
        """
        return {
            'filename': self.filename,
            'file_type': self.file_type.value,
            'extracted_text': self.extracted_text[:500],  # Truncate for brevity
            'skills': [skill.to_dict() for skill in self.skills],
            'user_name': self.user_name,
            'email': self.email,
            'phone': self.phone,
            'skill_count': self.skill_count
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"Resume({self.filename}, {self.skill_count} skills)"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Resume(filename='{self.filename}', file_type={self.file_type}, "
                f"skills={self.skill_count}, user_name='{self.user_name}')")


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create resume
    resume = Resume(filename="john_doe_resume.pdf", file_type=FileType.PDF)
    
    # Add skills
    resume.add_skill(Skill("Python", "Programming Language"))
    resume.add_skill(Skill("Java", "Programming Language"))
    resume.add_skill(Skill("Python", "Programming Language"))  # Duplicate - will increment frequency
    
    # Test properties
    print(f"Total skills: {resume.skill_count}")
    print(f"Skills: {resume.get_skills_as_string()}")
    print(f"Has Java: {resume.has_skill('java')}")
    
    # Get summary
    print("\n" + resume.get_summary())