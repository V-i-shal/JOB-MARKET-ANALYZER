"""
Job Model
Represents a job posting from the market
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .skill import Skill


@dataclass
class Job:
    """
    Represents a job posting from the job market.
    
    Attributes:
        title: Job title (e.g., "Senior Java Developer")
        company: Company name
        description: Full job description text
        required_skills: List of skills required for the job
        location: Job location
        salary: Salary information (if available)
        url: URL to job posting
        posted_date: Date when job was posted
    """
    
    title: str
    company: str
    description: str = ""
    required_skills: List[Skill] = field(default_factory=list)
    location: Optional[str] = None
    salary: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[str] = None
    
    @property
    def skill_count(self) -> int:
        """Returns the total number of required skills"""
        return len(self.required_skills)
    
    @property
    def technical_skills(self) -> List[Skill]:
        """Returns only technical skills"""
        return [skill for skill in self.required_skills if skill.is_technical]
    
    @property
    def soft_skills(self) -> List[Skill]:
        """Returns only soft skills"""
        return [skill for skill in self.required_skills if not skill.is_technical]
    
    def add_required_skill(self, skill: Skill) -> None:
        """
        Add a required skill to the job. If skill exists, increment frequency.
        
        Args:
            skill: Skill object to add
        """
        # Check if skill already exists
        for existing_skill in self.required_skills:
            if existing_skill.matches(skill):
                existing_skill.increment_frequency()
                return
        
        # Add new skill
        self.required_skills.append(skill)
    
    def requires_skill(self, skill_name: str) -> bool:
        """
        Check if job requires a specific skill.
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            True if skill is required, False otherwise
        """
        return any(skill.matches_name(skill_name) for skill in self.required_skills)
    
    def get_required_skills_as_string(self) -> str:
        """
        Get comma-separated list of required skill names.
        
        Returns:
            String like "Python, Java, SQL"
        """
        return ", ".join(skill.name for skill in self.required_skills)
    
    def calculate_match_percentage(self, user_skills: List[Skill]) -> float:
        """
        Calculate how well user skills match job requirements.
        
        Args:
            user_skills: List of skills the user has
            
        Returns:
            Match percentage (0-100)
        """
        if not self.required_skills:
            return 0.0
        
        # Convert user skills to set of lowercase names for fast lookup
        user_skill_names = {skill.name.lower() for skill in user_skills}
        
        # Count matching skills
        matching_count = sum(
            1 for skill in self.required_skills 
            if skill.name.lower() in user_skill_names
        )
        
        # Calculate percentage
        match_percentage = (matching_count / len(self.required_skills)) * 100
        return round(match_percentage, 2)
    
    def get_missing_skills(self, user_skills: List[Skill]) -> List[Skill]:
        """
        Get skills required by job but not present in user's skillset.
        
        Args:
            user_skills: List of skills the user has
            
        Returns:
            List of missing skills
        """
        user_skill_names = {skill.name.lower() for skill in user_skills}
        
        return [
            skill for skill in self.required_skills 
            if skill.name.lower() not in user_skill_names
        ]
    
    def get_matching_skills(self, user_skills: List[Skill]) -> List[Skill]:
        """
        Get skills that match between job requirements and user skills.
        
        Args:
            user_skills: List of skills the user has
            
        Returns:
            List of matching skills
        """
        user_skill_names = {skill.name.lower() for skill in user_skills}
        
        return [
            skill for skill in self.required_skills 
            if skill.name.lower() in user_skill_names
        ]
    
    def get_summary(self) -> str:
        """
        Get a summary of the job posting.
        
        Returns:
            Formatted summary string
        """
        return (f"Job: {self.title}\n"
                f"Company: {self.company}\n"
                f"Location: {self.location or 'Not specified'}\n"
                f"Salary: {self.salary or 'Not specified'}\n"
                f"Required Skills: {self.skill_count}\n"
                f"Technical: {len(self.technical_skills)}\n"
                f"Soft Skills: {len(self.soft_skills)}")
    
    def to_dict(self) -> dict:
        """
        Convert job to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of job
        """
        return {
            'title': self.title,
            'company': self.company,
            'description': self.description[:200],  # Truncate
            'required_skills': [skill.to_dict() for skill in self.required_skills],
            'location': self.location,
            'salary': self.salary,
            'url': self.url,
            'posted_date': self.posted_date,
            'skill_count': self.skill_count
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"Job({self.title} at {self.company}, {self.skill_count} skills required)"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Job(title='{self.title}', company='{self.company}', "
                f"location='{self.location}', skills={self.skill_count})")


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create job
    job = Job(
        title="Senior Python Developer",
        company="Tech Corp",
        location="San Francisco, CA",
        salary="$120k - $150k"
    )
    
    # Add required skills
    job.add_required_skill(Skill("Python", "Programming Language"))
    job.add_required_skill(Skill("Django", "Framework"))
    job.add_required_skill(Skill("PostgreSQL", "Database"))
    
    # User's skills
    user_skills = [
        Skill("Python", "Programming Language"),
        Skill("Flask", "Framework")
    ]
    
    # Calculate match
    match = job.calculate_match_percentage(user_skills)
    print(f"Match percentage: {match}%")
    
    # Get missing skills
    missing = job.get_missing_skills(user_skills)
    print(f"Missing skills: {[s.name for s in missing]}")
    
    # Get summary
    print("\n" + job.get_summary())