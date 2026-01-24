"""
Skill Extractor Service
Extracts technical skills from resume text using NLP and dictionary matching
"""

import re
from typing import List, Set
import spacy
from loguru import logger

# Import models
from ..models.skill import Skill


class SkillExtractor:
    """
    Extracts skills from text using two methods:
    1. Dictionary-based matching (fast, high precision)
    2. NLP-based extraction (using spaCy for context)
    """
    
    # Comprehensive skill dictionary (100+ skills)
    SKILL_DICTIONARY = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
        'swift', 'kotlin', 'go', 'golang', 'rust', 'scala', 'perl', 'r', 'matlab',
        'vba', 'objective-c', 'dart', 'elixir', 'haskell', 'clojure',
        
        # Web Technologies
        'html', 'css', 'html5', 'css3', 'sass', 'scss', 'less', 'xml', 'json',
        'ajax', 'rest', 'restful', 'graphql', 'websocket', 'soap',
        
        # Frontend Frameworks
        'react', 'angular', 'vue', 'vue.js', 'ember', 'backbone', 'jquery',
        'bootstrap', 'tailwind', 'material-ui', 'next.js', 'nuxt.js', 'svelte',
        
        # Backend Frameworks
        'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
        'laravel', 'symfony', 'rails', 'ruby on rails', 'asp.net', '.net', 'dotnet',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'mongodb', 'redis',
        'cassandra', 'dynamodb', 'elasticsearch', 'sqlite', 'mariadb', 'neo4j',
        'couchdb', 'influxdb',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
        'jenkins', 'gitlab', 'github actions', 'circleci', 'travis ci', 'terraform',
        'ansible', 'puppet', 'chef', 'vagrant', 'heroku', 'digitalocean', 'nginx',
        'apache',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn',
        'jupyter', 'anaconda', 'spark', 'hadoop', 'hive', 'pig', 'data analysis',
        'data science', 'nlp', 'computer vision', 'neural networks', 'cnn', 'rnn',
        'lstm', 'bert', 'transformers',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova',
        'ionic', 'swift ui', 'jetpack compose',
        
        # Testing
        'unit testing', 'integration testing', 'pytest', 'junit', 'selenium',
        'cypress', 'jest', 'mocha', 'chai', 'testng', 'cucumber',
        
        # Version Control
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
        
        # Methodologies
        'agile', 'scrum', 'kanban', 'waterfall', 'ci/cd', 'tdd', 'bdd', 'devops',
        
        # Other Tools
        'linux', 'unix', 'bash', 'shell scripting', 'powershell', 'vim', 'emacs',
        'vscode', 'intellij', 'eclipse', 'pycharm', 'postman', 'swagger', 'jira',
        'confluence', 'slack', 'trello', 'notion',
        
        # Big Data
        'kafka', 'rabbitmq', 'airflow', 'flink', 'storm', 'etl',
        
        # Security
        'oauth', 'jwt', 'ssl', 'tls', 'encryption', 'cybersecurity', 'penetration testing',
        
        # Soft Skills (marked as non-technical)
        'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
        'project management', 'time management', 'critical thinking'
    }
    
    # Words to exclude (common false positives)
    EXCLUDED_WORDS = {
        'experience', 'years', 'months', 'customer', 'date', 'time', 'work',
        'project', 'team', 'company', 'position', 'role', 'skills', 'education',
        'university', 'college', 'school', 'degree', 'bachelor', 'master', 'phd'
    }
    
    # Skill categories mapping
    SKILL_CATEGORIES = {
        # Programming Languages
        'python': 'Programming Language',
        'java': 'Programming Language',
        'javascript': 'Programming Language',
        'typescript': 'Programming Language',
        'c++': 'Programming Language',
        'c#': 'Programming Language',
        'ruby': 'Programming Language',
        'php': 'Programming Language',
        'go': 'Programming Language',
        'golang': 'Programming Language',
        'rust': 'Programming Language',
        
        # Frameworks
        'react': 'Frontend Framework',
        'angular': 'Frontend Framework',
        'vue': 'Frontend Framework',
        'django': 'Backend Framework',
        'flask': 'Backend Framework',
        'spring': 'Backend Framework',
        'spring boot': 'Backend Framework',
        'express': 'Backend Framework',
        'node.js': 'Backend Framework',
        
        # Databases
        'sql': 'Database',
        'mysql': 'Database',
        'postgresql': 'Database',
        'mongodb': 'Database',
        'redis': 'Database',
        'oracle': 'Database',
        
        # Cloud
        'aws': 'Cloud Platform',
        'azure': 'Cloud Platform',
        'gcp': 'Cloud Platform',
        'google cloud': 'Cloud Platform',
        
        # DevOps
        'docker': 'DevOps Tool',
        'kubernetes': 'DevOps Tool',
        'jenkins': 'DevOps Tool',
        'terraform': 'DevOps Tool',
        
        # ML/AI
        'machine learning': 'Machine Learning',
        'tensorflow': 'Machine Learning',
        'pytorch': 'Machine Learning',
        'keras': 'Machine Learning',
        
        # Soft Skills
        'leadership': 'Soft Skill',
        'communication': 'Soft Skill',
        'teamwork': 'Soft Skill',
        'problem solving': 'Soft Skill'
    }
    
    # Soft skills list
    SOFT_SKILLS = {
        'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'project management', 'time management', 'critical thinking'
    }
    
    def __init__(self):
        """Initialize the skill extractor with spaCy model"""
        try:
            # Load spaCy English model
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found!")
            logger.info("Download with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_skills(self, text: str) -> List[Skill]:
        """
        Main method to extract skills from text.
        Uses both dictionary-based and NLP-based methods.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of Skill objects
        """
        if not text or len(text.strip()) < 10:
            logger.warning("Text too short for skill extraction")
            return []
        
        try:
            # Method 1: Dictionary-based extraction (fast, high precision)
            dict_skills = self._extract_skills_dictionary(text)
            logger.info(f"Dictionary method found {len(dict_skills)} skills")
            
            # Method 2: NLP-based extraction (slower, higher recall)
            nlp_skills = set()
            if self.nlp:
                nlp_skills = self._extract_skills_nlp(text)
                logger.info(f"NLP method found {len(nlp_skills)} skills")
            
            # Combine results (union of both methods)
            all_skill_names = dict_skills.union(nlp_skills)
            
            # Create Skill objects with proper categorization
            skills = []
            for skill_name in all_skill_names:
                skill_lower = skill_name.lower()
                
                # Determine category
                category = self.SKILL_CATEGORIES.get(skill_lower, 'Technical')
                
                # Determine if technical or soft skill
                is_technical = skill_lower not in self.SOFT_SKILLS
                
                # Count frequency in text
                frequency = self._count_skill_frequency(text, skill_name)
                
                skill = Skill(
                    name=skill_name,
                    category=category,
                    is_technical=is_technical,
                    frequency=frequency
                )
                skills.append(skill)
            
            # Sort by frequency (most common first)
            skills.sort(key=lambda s: s.frequency, reverse=True)
            
            logger.info(f"Total unique skills extracted: {len(skills)}")
            return skills
            
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []
    
    def _extract_skills_dictionary(self, text: str) -> Set[str]:
        """
        Extract skills using dictionary matching.
        
        Args:
            text: Text to search
            
        Returns:
            Set of skill names found
        """
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.SKILL_DICTIONARY:
            # Skip excluded words
            if skill in self.EXCLUDED_WORDS:
                continue
            
            # Check if skill exists in text
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly for display
                found_skills.add(skill.title())
        
        return found_skills
    
    def _extract_skills_nlp(self, text: str) -> Set[str]:
        """
        Extract skills using NLP (spaCy).
        Identifies nouns and noun phrases that match known skills.
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of skill names found
        """
        if not self.nlp:
            return set()
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            found_skills = set()
            
            # Extract noun chunks (multi-word skills like "machine learning")
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if chunk_text in self.SKILL_DICTIONARY and chunk_text not in self.EXCLUDED_WORDS:
                    found_skills.add(chunk_text.title())
            
            # Extract individual nouns
            for token in doc:
                # Look for nouns and proper nouns
                if token.pos_ in ['NOUN', 'PROPN']:
                    token_text = token.text.lower().strip()
                    if token_text in self.SKILL_DICTIONARY and token_text not in self.EXCLUDED_WORDS:
                        found_skills.add(token_text.title())
            
            return found_skills
            
        except Exception as e:
            logger.error(f"Error in NLP extraction: {e}")
            return set()
    
    def _count_skill_frequency(self, text: str, skill_name: str) -> int:
        """
        Count how many times a skill appears in text.
        
        Args:
            text: Text to search
            skill_name: Skill to count
            
        Returns:
            Frequency count
        """
        text_lower = text.lower()
        skill_lower = skill_name.lower()
        
        # Use word boundaries for accurate counting
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        matches = re.findall(pattern, text_lower)
        
        return len(matches)
    
    def extract_skills_from_list(self, skill_list: List[str]) -> List[Skill]:
        """
        Convert a list of skill names to Skill objects.
        Useful for processing job requirements.
        
        Args:
            skill_list: List of skill name strings
            
        Returns:
            List of Skill objects
        """
        skills = []
        for skill_name in skill_list:
            skill_lower = skill_name.lower().strip()
            
            if not skill_lower or skill_lower in self.EXCLUDED_WORDS:
                continue
            
            category = self.SKILL_CATEGORIES.get(skill_lower, 'Technical')
            is_technical = skill_lower not in self.SOFT_SKILLS
            
            skill = Skill(
                name=skill_name.strip().title(),
                category=category,
                is_technical=is_technical,
                frequency=1
            )
            skills.append(skill)
        
        return skills
    
    def validate_skill(self, skill_name: str) -> bool:
        """
        Check if a skill name is in the dictionary.
        
        Args:
            skill_name: Skill to validate
            
        Returns:
            True if valid skill, False otherwise
        """
        return skill_name.lower() in self.SKILL_DICTIONARY


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/skill_extractor.log", rotation="10 MB")
    
    print("=" * 60)
    print("SKILL EXTRACTOR TEST")
    print("=" * 60)
    
    # Create extractor
    extractor = SkillExtractor()
    
    # Test with sample resume text
    sample_text = """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567
    
    SUMMARY
    Experienced software engineer with 5 years of Python and Java development.
    Strong background in machine learning, cloud computing, and web development.
    
    SKILLS
    - Programming: Python, Java, JavaScript, TypeScript
    - Frameworks: Django, Flask, React, Node.js, Spring Boot
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Docker, Kubernetes
    - ML/AI: TensorFlow, PyTorch, scikit-learn, pandas, numpy
    - Tools: Git, Jenkins, JIRA
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    - Developed microservices using Python and Docker
    - Implemented CI/CD pipelines with Jenkins and Kubernetes
    - Built machine learning models using TensorFlow
    - Worked with AWS services (EC2, S3, Lambda)
    
    Software Engineer | StartupXYZ | 2018-2020
    - Built REST APIs with Django and Flask
    - Developed frontend applications using React and TypeScript
    - Managed PostgreSQL and MongoDB databases
    - Collaborated using Git and Agile methodologies
    """
    
    print("\n1. Extracting skills from sample text...")
    skills = extractor.extract_skills(sample_text)
    
    print(f"\n✓ Found {len(skills)} skills:\n")
    
    # Group by category
    from collections import defaultdict
    skills_by_category = defaultdict(list)
    for skill in skills:
        skills_by_category[skill.category].append(skill)
    
    # Display grouped skills
    for category in sorted(skills_by_category.keys()):
        print(f"\n{category}:")
        for skill in skills_by_category[category]:
            print(f"  • {skill.name} (frequency: {skill.frequency})")
    
    # Test skill validation
    print("\n2. Testing skill validation...")
    test_skills = ["Python", "Docker", "InvalidSkill123", "React"]
    for test_skill in test_skills:
        is_valid = extractor.validate_skill(test_skill)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {test_skill}: {is_valid}")
    
    print("\n" + "=" * 60)
    print("Skill extractor tests completed!")
    print("=" * 60)