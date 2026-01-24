"""
Analysis Result Model
Contains complete analysis results after processing resume and jobs
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .resume import Resume
from .job import Job
from .skill import Skill
from .learning_resource import LearningResource


@dataclass
class AnalysisResult:
    """
    Contains complete analysis results.
    
    Attributes:
        resume: User's resume object
        analyzed_jobs: List of jobs analyzed
        matching_skills: Skills user has that match job requirements
        missing_skills: Skills user needs to learn
        match_percentage: Overall match percentage (0-100)
        recommended_resources: Learning materials for missing skills
        learning_path: Generated 4-week learning plan (text)
        cluster_id: K-Means cluster ID (career path indicator)
        jobs_in_same_cluster: Number of jobs in same cluster as resume
    """
    
    resume: Resume
    analyzed_jobs: List[Job] = field(default_factory=list)
    matching_skills: List[Skill] = field(default_factory=list)
    missing_skills: List[Skill] = field(default_factory=list)
    match_percentage: float = 0.0
    recommended_resources: List[LearningResource] = field(default_factory=list)
    learning_path: str = ""
    cluster_id: Optional[int] = None
    jobs_in_same_cluster: int = 0
    
    @property
    def total_jobs_analyzed(self) -> int:
        """Returns total number of jobs analyzed"""
        return len(self.analyzed_jobs)
    
    @property
    def matching_skill_count(self) -> int:
        """Returns count of matching skills"""
        return len(self.matching_skills)
    
    @property
    def missing_skill_count(self) -> int:
        """Returns count of missing skills"""
        return len(self.missing_skills)
    
    @property
    def top_missing_skills(self) -> List[Skill]:
        """
        Returns top 10 missing skills sorted by frequency (most demanded).
        """
        sorted_skills = sorted(
            self.missing_skills, 
            key=lambda s: s.frequency, 
            reverse=True
        )
        return sorted_skills[:10]
    
    def add_matching_skill(self, skill: Skill) -> None:
        """
        Add a skill to matching skills list.
        
        Args:
            skill: Skill to add
        """
        # Avoid duplicates
        if not any(s.matches(skill) for s in self.matching_skills):
            self.matching_skills.append(skill)
    
    def add_missing_skill(self, skill: Skill) -> None:
        """
        Add a skill to missing skills list.
        
        Args:
            skill: Skill to add
        """
        # Check if skill already exists, if so increment frequency
        for existing in self.missing_skills:
            if existing.matches(skill):
                existing.increment_frequency()
                return
        
        # Add new skill
        skill.frequency = 1
        self.missing_skills.append(skill)
    
    def calculate_match_percentage(self) -> float:
        """
        Calculate overall match percentage based on skills.
        
        Returns:
            Match percentage (0-100)
        """
        if not self.matching_skills and not self.missing_skills:
            return 0.0
        
        total_skills = len(self.matching_skills) + len(self.missing_skills)
        if total_skills == 0:
            return 0.0
        
        match = (len(self.matching_skills) / total_skills) * 100
        self.match_percentage = round(match, 2)
        return self.match_percentage
    
    def get_matching_skills_as_string(self) -> str:
        """
        Get comma-separated list of matching skill names.
        
        Returns:
            String like "Python, Java, SQL"
        """
        return ", ".join(skill.name for skill in self.matching_skills)
    
    def get_missing_skills_as_string(self) -> str:
        """
        Get comma-separated list of missing skill names.
        
        Returns:
            String like "Docker, Kubernetes, AWS"
        """
        return ", ".join(skill.name for skill in self.missing_skills)
    
    def get_summary(self) -> str:
        """
        Get one-line summary of analysis.
        
        Returns:
            Summary string
        """
        return (f"Analyzed {self.total_jobs_analyzed} jobs: "
                f"{self.match_percentage}% match, "
                f"{self.matching_skill_count} skills found, "
                f"{self.missing_skill_count} skills to learn")
    
    def get_detailed_summary(self) -> str:
        """
        Get detailed multi-line summary.
        
        Returns:
            Formatted summary string
        """
        summary = [
            "=" * 60,
            "ANALYSIS SUMMARY",
            "=" * 60,
            f"Resume: {self.resume.filename}",
            f"Jobs Analyzed: {self.total_jobs_analyzed}",
            f"Overall Match: {self.match_percentage}%",
            "",
            f"✓ Matching Skills ({self.matching_skill_count}):",
            f"  {self.get_matching_skills_as_string()}",
            "",
            f"✗ Missing Skills ({self.missing_skill_count}):",
            f"  {self.get_missing_skills_as_string()}",
            "",
            f"Recommended Resources: {len(self.recommended_resources)}",
            "=" * 60
        ]
        return "\n".join(summary)
    
    def to_dict(self) -> dict:
        """
        Convert analysis result to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'resume': self.resume.to_dict(),
            'total_jobs_analyzed': self.total_jobs_analyzed,
            'matching_skills': [s.to_dict() for s in self.matching_skills],
            'missing_skills': [s.to_dict() for s in self.missing_skills],
            'match_percentage': self.match_percentage,
            'recommended_resources': [r.to_dict() for r in self.recommended_resources],
        }