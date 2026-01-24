"""
Learning Resource Model
Represents a course or learning material
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Platform(Enum):
    """Enum for learning platforms"""
    UDEMY = "Udemy"
    COURSERA = "Coursera"
    YOUTUBE = "YouTube"
    PLURALSIGHT = "Pluralsight"
    LINKEDIN_LEARNING = "LinkedIn Learning"
    EDEX = "edX"
    FREECODECAMP = "freeCodeCamp"
    OTHER = "Other"


class DifficultyLevel(Enum):
    """Enum for course difficulty levels"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ALL_LEVELS = "All Levels"


@dataclass
class LearningResource:
    """
    Represents a course or learning material.
    
    Attributes:
        skill_name: Skill this resource teaches
        resource_title: Course/resource title
        resource_url: Link to the resource
        platform: Learning platform (Udemy, Coursera, etc.)
        duration_weeks: Estimated time to complete (in weeks)
        difficulty_level: Beginner/Intermediate/Advanced
        description: Brief description of the resource
        rating: User rating (0-5)
        price: Price information (free, $, $$, $$$)
    """
    
    skill_name: str
    resource_title: str
    resource_url: str
    platform: Platform = Platform.OTHER
    duration_weeks: int = 1
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    description: Optional[str] = None
    rating: Optional[float] = None
    price: str = "Free"
    
    def is_for_beginners(self) -> bool:
        """
        Check if resource is suitable for beginners.
        
        Returns:
            True if beginner-friendly, False otherwise
        """
        return self.difficulty_level in [
            DifficultyLevel.BEGINNER, 
            DifficultyLevel.ALL_LEVELS
        ]
    
    def fits_in_timeframe(self, max_weeks: int) -> bool:
        """
        Check if resource can be completed within given timeframe.
        
        Args:
            max_weeks: Maximum weeks available
            
        Returns:
            True if resource fits, False otherwise
        """
        return self.duration_weeks <= max_weeks
    
    def is_free(self) -> bool:
        """Check if resource is free"""
        return self.price.lower() in ["free", "$0", "0"]
    
    def get_display_string(self) -> str:
        """
        Get formatted string for UI display.
        
        Returns:
            Formatted string like "Python Masterclass (Udemy) - 4 weeks"
        """
        return (f"{self.resource_title} ({self.platform.value}) - "
                f"{self.duration_weeks} week{'s' if self.duration_weeks > 1 else ''}, "
                f"{self.difficulty_level.value}")
    
    def get_markdown_link(self) -> str:
        """
        Get resource as markdown link.
        
        Returns:
            Markdown formatted link
        """
        return f"[{self.resource_title}]({self.resource_url})"
    
    def to_dict(self) -> dict:
        """
        Convert learning resource to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'skill_name': self.skill_name,
            'resource_title': self.resource_title,
            'resource_url': self.resource_url,
            'platform': self.platform.value,
            'duration_weeks': self.duration_weeks,
            'difficulty_level': self.difficulty_level.value,
            'description': self.description,
            'rating': self.rating,
            'price': self.price
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LearningResource':
        """
        Create LearningResource from dictionary.
        
        Args:
            data: Dictionary containing resource data
            
        Returns:
            New LearningResource instance
        """
        # Convert string platform to enum
        platform_str = data.get('platform', 'Other')
        try:
            platform = Platform(platform_str)
        except ValueError:
            platform = Platform.OTHER
        
        # Convert string difficulty to enum
        difficulty_str = data.get('difficulty_level', 'Beginner')
        try:
            difficulty = DifficultyLevel(difficulty_str)
        except ValueError:
            difficulty = DifficultyLevel.BEGINNER
        
        return cls(
            skill_name=data.get('skill_name', ''),
            resource_title=data.get('resource_title', ''),
            resource_url=data.get('resource_url', ''),
            platform=platform,
            duration_weeks=data.get('duration_weeks', 1),
            difficulty_level=difficulty,
            description=data.get('description'),
            rating=data.get('rating'),
            price=data.get('price', 'Free')
        )
    
    def __str__(self) -> str:
        """String representation"""
        return f"LearningResource({self.resource_title}, {self.platform.value})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"LearningResource(skill='{self.skill_name}', "
                f"title='{self.resource_title}', platform={self.platform.value})")


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create learning resource
    resource = LearningResource(
        skill_name="Python",
        resource_title="Python for Beginners",
        resource_url="https://www.udemy.com/course/python-beginners",
        platform=Platform.UDEMY,
        duration_weeks=3,
        difficulty_level=DifficultyLevel.BEGINNER,
        rating=4.7,
        price="$19.99"
    )
    
    # Test methods
    print(f"Is for beginners: {resource.is_for_beginners()}")
    print(f"Fits in 4 weeks: {resource.fits_in_timeframe(4)}")
    print(f"Display: {resource.get_display_string()}")
    print(f"Markdown: {resource.get_markdown_link()}")