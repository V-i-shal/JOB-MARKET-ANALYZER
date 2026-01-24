"""
Learning Path Generator Service
Generates personalized 4-week learning plans based on skill gaps
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

# Import models and services
# Import models and services (relative import)
from ..models.analysis_result import AnalysisResult
from ..models.skill import Skill
from ..models.learning_resource import LearningResource
from .database_manager import DatabaseManager


class LearningPathGenerator:
    """
    Generates personalized 4-week learning paths.
    Distributes missing skills across 4 weeks with resources and milestones.
    """
    
    def __init__(self):
        """Initialize the learning path generator"""
        self.db = DatabaseManager()
        logger.info("LearningPathGenerator initialized")
    
    def generate_learning_path(self, result: AnalysisResult) -> str:
        """
        Generate a complete 4-week learning path.
        
        Args:
            result: AnalysisResult containing missing skills
            
        Returns:
            Formatted learning path as string
        """
        if not result.missing_skills:
            logger.info("No missing skills - no learning path needed")
            return self._generate_no_gaps_message(result)
        
        try:
            logger.info(f"Generating learning path for {len(result.missing_skills)} missing skills")
            
            # Step 1: Prioritize and limit skills (top 8 skills, 2 per week)
            priority_skills = self._prioritize_skills(result.missing_skills, max_skills=8)
            
            # Step 2: Fetch learning resources for each skill
            skill_resources = self._fetch_resources_for_skills(priority_skills)
            
            # Step 3: Distribute skills across 4 weeks
            weekly_plan = self._distribute_skills_across_weeks(priority_skills, skill_resources)
            
            # Step 4: Format the learning path
            learning_path = self._format_learning_path(weekly_plan, result)
            
            # Step 5: Store resources in AnalysisResult
            for resources in skill_resources.values():
                result.recommended_resources.extend(resources)
            
            logger.info("Learning path generated successfully")
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return f"Error generating learning path: {str(e)}"
    
    def _prioritize_skills(self, skills: List[Skill], max_skills: int = 8) -> List[Skill]:
        """
        Prioritize skills by importance (frequency in job postings).
        
        Args:
            skills: List of missing skills
            max_skills: Maximum number of skills to include
            
        Returns:
            Prioritized list of skills
        """
        # Skills are already sorted by frequency in SkillAnalyzer
        priority_skills = skills[:max_skills]
        
        logger.info(f"Prioritized top {len(priority_skills)} skills for learning path")
        return priority_skills
    
    def _fetch_resources_for_skills(
        self,
        skills: List[Skill]
    ) -> Dict[str, List[LearningResource]]:
        """
        Fetch learning resources for each skill from database.
        
        Args:
            skills: List of skills to fetch resources for
            
        Returns:
            Dictionary mapping skill names to their resources
        """
        skill_resources = {}
        
        for skill in skills:
            # Fetch from database
            db_resources = self.db.get_learning_resources_by_skill(
                skill.name,
                limit=3  # Get top 3 resources per skill
            )
            
            # Convert to LearningResource objects
            resources = []
            for row in db_resources:
                resource = LearningResource(
                    skill_name=row['skill_name'],
                    resource_title=row['resource_title'],
                    resource_url=row['resource_url'],
                    platform=self._parse_platform(row['platform']),
                    duration_weeks=row['duration_weeks'] or 1,
                    difficulty_level=self._parse_difficulty(row['difficulty_level']),
                    description=row['description'],
                    rating=row['rating'],
                    price=row['price'] or 'Free'
                )
                resources.append(resource)
            
            skill_resources[skill.name] = resources
            logger.debug(f"Found {len(resources)} resources for {skill.name}")
        
        return skill_resources
    
    def _parse_platform(self, platform_str: str):
        """Parse platform string to Platform enum"""
        from ..models.learning_resource import Platform
        try:
            return Platform(platform_str)
        except ValueError:
            return Platform.OTHER
    
    def _parse_difficulty(self, difficulty_str: str):
        """Parse difficulty string to DifficultyLevel enum"""
        from ..models.learning_resource import DifficultyLevel
        try:
            return DifficultyLevel(difficulty_str)
        except ValueError:
            return DifficultyLevel.BEGINNER
    
    def _distribute_skills_across_weeks(
        self,
        skills: List[Skill],
        skill_resources: Dict[str, List[LearningResource]]
    ) -> List[Dict]:
        """
        Distribute skills across 4 weeks (2 skills per week).
        
        Args:
            skills: Prioritized list of skills
            skill_resources: Resources for each skill
            
        Returns:
            List of weekly plans (4 weeks)
        """
        weekly_plan = []
        skills_per_week = 2
        
        for week in range(1, 5):  # 4 weeks
            start_idx = (week - 1) * skills_per_week
            end_idx = start_idx + skills_per_week
            week_skills = skills[start_idx:end_idx]
            
            if not week_skills:
                break  # No more skills to assign
            
            week_data = {
                'week_number': week,
                'skills': week_skills,
                'resources': {},
                'milestones': self._generate_milestones(week, week_skills)
            }
            
            # Add resources for each skill
            for skill in week_skills:
                week_data['resources'][skill.name] = skill_resources.get(skill.name, [])
            
            weekly_plan.append(week_data)
        
        return weekly_plan
    
    def _generate_milestones(self, week: int, skills: List[Skill]) -> List[str]:
        """
        Generate achievement milestones for a week.
        
        Args:
            week: Week number
            skills: Skills for this week
            
        Returns:
            List of milestone descriptions
        """
        milestones = []
        
        for skill in skills:
            milestones.append(f"Complete {skill.name} tutorial/course")
            milestones.append(f"Build a small project using {skill.name}")
        
        milestones.append("Document your learning progress")
        milestones.append("Update your resume with new skills")
        
        return milestones
    
    def _format_learning_path(
        self,
        weekly_plan: List[Dict],
        result: AnalysisResult
    ) -> str:
        """
        Format the learning path as a nice text output.
        
        Args:
            weekly_plan: List of weekly plan dictionaries
            result: Analysis result for context
            
        Returns:
            Formatted learning path string
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("YOUR PERSONALIZED 4-WEEK LEARNING PATH")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Overall Match: {result.match_percentage}%")
        lines.append(f"Skills to Learn: {len(result.missing_skills)}")
        lines.append("")
        
        # Weekly breakdown
        for week_data in weekly_plan:
            week = week_data['week_number']
            skills = week_data['skills']
            resources = week_data['resources']
            milestones = week_data['milestones']
            
            lines.append("─" * 70)
            lines.append(f"📅 WEEK {week}")
            lines.append("─" * 70)
            lines.append("")
            
            # Skills focus
            skill_names = [s.name for s in skills]
            lines.append(f"🎯 Focus Skills: {', '.join(skill_names)}")
            lines.append("")
            
            # Resources for each skill
            for skill in skills:
                lines.append(f"📖 {skill.name} Learning Resources:")
                skill_resources = resources.get(skill.name, [])
                
                if skill_resources:
                    for i, resource in enumerate(skill_resources[:2], 1):  # Show top 2
                        lines.append(f"   {i}. {resource.resource_title} ({resource.platform.value})")
                        lines.append(f"      ↳ {resource.resource_url}")
                        if resource.rating:
                            lines.append(f"      ⭐ Rating: {resource.rating}/5.0 | "
                                       f"Duration: {resource.duration_weeks} week(s) | "
                                       f"Level: {resource.difficulty_level.value}")
                else:
                    lines.append(f"   • Search online for '{skill.name} tutorial'")
                    lines.append(f"   • Check platforms: Udemy, Coursera, YouTube")
                
                lines.append("")
            
            # Milestones
            lines.append(f"🏆 Week {week} Milestones:")
            for i, milestone in enumerate(milestones[:4], 1):  # Show top 4
                lines.append(f"   {i}. {milestone}")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("💡 TIPS FOR SUCCESS")
        lines.append("=" * 70)
        lines.append("")
        lines.append("• Dedicate 1-2 hours daily to learning")
        lines.append("• Build projects to reinforce concepts")
        lines.append("• Join online communities (Stack Overflow, Reddit, Discord)")
        lines.append("• Document your progress on GitHub")
        lines.append("• Update your resume as you learn new skills")
        lines.append("• Don't rush - deep understanding beats speed")
        lines.append("")
        lines.append("=" * 70)
        lines.append("Good luck on your learning journey! 🚀")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _generate_no_gaps_message(self, result: AnalysisResult) -> str:
        """
        Generate message when no skill gaps are found.
        
        Args:
            result: Analysis result
            
        Returns:
            Congratulatory message
        """
        lines = []
        lines.append("=" * 70)
        lines.append("🎉 CONGRATULATIONS!")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Overall Match: {result.match_percentage}%")
        lines.append("")
        lines.append("You already have all the key skills required for the analyzed jobs!")
        lines.append("Consider focusing on:")
        lines.append("")
        lines.append("• Advanced topics in your existing skills")
        lines.append("• Emerging technologies in your field")
        lines.append("• Leadership and soft skills development")
        lines.append("• Building a strong portfolio of projects")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_learning_path(
        self,
        analysis_id: int,
        learning_path: str,
        result: AnalysisResult
    ) -> bool:
        """
        Save learning path to database.
        
        Args:
            analysis_id: ID of the analysis record
            learning_path: Full learning path text
            result: Analysis result
            
        Returns:
            True if successful
        """
        try:
            # Parse weekly data from result (we could store this separately)
            # For now, we'll store a simplified version
            
            priority_skills = result.missing_skills[:8]
            skills_per_week = 2
            
            for week in range(1, 5):
                start_idx = (week - 1) * skills_per_week
                end_idx = start_idx + skills_per_week
                week_skills = priority_skills[start_idx:end_idx]
                
                if not week_skills:
                    break
                
                skill_focus = ", ".join([s.name for s in week_skills])
                resources = "See learning path for details"
                milestones = "; ".join(self._generate_milestones(week, week_skills)[:3])
                
                self.db.save_learning_path(
                    analysis_id=analysis_id,
                    week_number=week,
                    skill_focus=skill_focus,
                    resources=resources,
                    milestones=milestones
                )
            
            logger.info(f"Learning path saved for analysis ID: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving learning path: {e}")
            return False


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/learning_path_generator.log", rotation="10 MB")
    
    print("=" * 70)
    print("LEARNING PATH GENERATOR TEST")
    print("=" * 70)
    
    # Create sample analysis result
    from models.resume import Resume, FileType
    resume = Resume(filename="test.pdf", file_type=FileType.PDF)
    
    result = AnalysisResult(resume=resume)
    result.match_percentage = 65.0
    
    # Add missing skills (sorted by frequency)
    missing_skills_data = [
        ("Docker", 35),
        ("Kubernetes", 28),
        ("AWS", 42),
        ("React", 25),
        ("TypeScript", 20),
        ("MongoDB", 18),
        ("Redis", 15),
        ("GraphQL", 12),
        ("TensorFlow", 10),
        ("Jenkins", 8)
    ]
    
    for skill_name, freq in missing_skills_data:
        skill = Skill(skill_name, "Technical", frequency=freq)
        result.add_missing_skill(skill)
    
    # Generate learning path
    generator = LearningPathGenerator()
    learning_path = generator.generate_learning_path(result)
    
    # Display
    print("\n" + learning_path)
    
    print("\n" + "=" * 70)
    print("Learning path generator tests completed!")
    print("=" * 70)