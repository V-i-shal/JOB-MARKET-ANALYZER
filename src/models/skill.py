"""
Skill Model
Represents a single skill with metadata
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Skill:
    """
    Represents a single skill (e.g., "Java", "Python")
    
    Attributes:
        name: Skill name (e.g., "Python")
        category: Skill category (e.g., "Programming Language", "Framework")
        is_technical: Whether it's a technical skill (True) or soft skill (False)
        frequency: How many times this skill appears in resume/job description
    """
    
    name: str
    category: str = "Technical"
    is_technical: bool = True
    frequency: int = 0
    
    def __post_init__(self):
        """Normalize skill name after initialization"""
        # Convert to title case for consistency
        self.name = self.name.strip().title()
    
    def increment_frequency(self) -> None:
        """
        Increases the frequency count by 1.
        Used when skill is found multiple times in text.
        """
        self.frequency += 1
    
    def matches(self, other: 'Skill') -> bool:
        """
        Check if this skill matches another skill (case-insensitive).
        
        Args:
            other: Another Skill object to compare with
            
        Returns:
            True if skill names match (case-insensitive), False otherwise
        """
        return self.name.lower() == other.name.lower()
    
    def matches_name(self, name: str) -> bool:
        """
        Check if this skill matches a given name (case-insensitive).
        
        Args:
            name: Skill name as string
            
        Returns:
            True if names match, False otherwise
        """
        return self.name.lower() == name.lower().strip()
    
    def __eq__(self, other) -> bool:
        """
        Equality comparison for skills.
        Required for using Skill in sets and as dict keys.
        """
        if not isinstance(other, Skill):
            return False
        return self.name.lower() == other.name.lower()
    
    def __hash__(self) -> int:
        """
        Hash function for using Skill in sets and as dict keys.
        """
        return hash(self.name.lower())
    
    def __str__(self) -> str:
        """String representation of skill"""
        return f"{self.name} (freq: {self.frequency})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Skill(name='{self.name}', category='{self.category}', "
                f"is_technical={self.is_technical}, frequency={self.frequency})")
    
    def to_dict(self) -> dict:
        """
        Convert skill to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the skill
        """
        return {
            'name': self.name,
            'category': self.category,
            'is_technical': self.is_technical,
            'frequency': self.frequency
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        """
        Create Skill object from dictionary.
        
        Args:
            data: Dictionary containing skill data
            
        Returns:
            New Skill instance
        """
        return cls(
            name=data.get('name', ''),
            category=data.get('category', 'Technical'),
            is_technical=data.get('is_technical', True),
            frequency=data.get('frequency', 0)
        )


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create skills
    skill1 = Skill(name="python", category="Programming Language")
    skill2 = Skill(name="PYTHON", category="Programming Language")
    
    # Test matching
    print(f"skill1 matches skill2: {skill1.matches(skill2)}")  # True
    
    # Test frequency
    skill1.increment_frequency()
    skill1.increment_frequency()
    print(f"Skill: {skill1}")  # Python (freq: 2)
    
    # Test equality (for sets)
    print(f"skill1 == skill2: {skill1 == skill2}")  # True
    
    # Test in set (removes duplicates)
    skills_set = {skill1, skill2}
    print(f"Unique skills: {len(skills_set)}")  # 1 (duplicates removed)