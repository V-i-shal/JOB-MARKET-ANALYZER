"""
Database Manager Service
Singleton pattern for managing SQLite database operations
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from loguru import logger


class DatabaseManager:
    """
    Singleton class for managing SQLite database.
    Handles all database operations including CRUD for learning resources,
    analysis history, and learning paths.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Implement Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database connection and create tables"""
        if self._initialized:
            return
        
        self._initialized = True
        self.db_path = self._get_database_path()
        self._ensure_database_directory()
        self.connect()
        self.create_tables()
        self.insert_sample_resources()
        logger.info(f"DatabaseManager initialized with database at: {self.db_path}")
    
    def _get_database_path(self) -> str:
        """Get the database file path"""
        # Get project root directory
        current_dir = Path(__file__).resolve()
        project_root = current_dir.parent.parent.parent
        db_dir = project_root / "data"
        return str(db_dir / "jobanalyzer.db")
    
    def _ensure_database_directory(self) -> None:
        """Ensure the data directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database directory ensured: {db_dir}")
    
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Allow multi-threaded access
            )
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info("Database connection established")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Get the database connection"""
        if self._connection is None:
            self.connect()
        return self._connection
    
    def close(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is not None:
            self._connection.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            self._connection.commit()
        return False
    
    def create_tables(self) -> None:
        """Create all database tables if they don't exist"""
        try:
            cursor = self._connection.cursor()
            
            # Table 1: Learning Resources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    resource_title TEXT NOT NULL,
                    resource_url TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    duration_weeks INTEGER DEFAULT 1,
                    difficulty_level TEXT DEFAULT 'Beginner',
                    description TEXT,
                    rating REAL,
                    price TEXT DEFAULT 'Free',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 2: Skills Master List
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills_master (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT UNIQUE NOT NULL,
                    category TEXT DEFAULT 'Technical',
                    is_technical BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 3: Analysis History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_filename TEXT NOT NULL,
                    user_name TEXT,
                    user_email TEXT,
                    extracted_skills TEXT,
                    missing_skills TEXT,
                    match_percentage REAL,
                    jobs_analyzed INTEGER,
                    cluster_id INTEGER,
                    jobs_in_same_cluster INTEGER,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 4: Learning Paths
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER,
                    week_number INTEGER,
                    skill_focus TEXT,
                    resources TEXT,
                    milestones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
                )
            """)
            
            self._connection.commit()
            logger.info("All database tables created successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_sample_resources(self) -> None:
        """Insert sample learning resources into database"""
        try:
            cursor = self._connection.cursor()
            
            # Check if resources already exist
            cursor.execute("SELECT COUNT(*) FROM learning_resources")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"Database already contains {count} resources, skipping insertion")
                return
            
            # Sample resources data
            resources = [
                # Python
                ("Python", "Complete Python Bootcamp", "https://www.udemy.com/course/complete-python-bootcamp/", 
                 "Udemy", 4, "Beginner", "Learn Python from scratch", 4.6, "$19.99"),
                ("Python", "Python for Everybody", "https://www.coursera.org/specializations/python", 
                 "Coursera", 8, "Beginner", "University of Michigan Python course", 4.8, "Free"),
                ("Python", "Python Tutorial", "https://www.youtube.com/watch?v=_uQrJ0TkZlc", 
                 "YouTube", 1, "Beginner", "6-hour Python tutorial", 4.7, "Free"),
                
                # Java
                ("Java", "Java Programming Masterclass", "https://www.udemy.com/course/java-the-complete-java-developer-course/", 
                 "Udemy", 6, "Beginner", "Complete Java development", 4.6, "$24.99"),
                ("Java", "Object Oriented Programming in Java", "https://www.coursera.org/learn/object-oriented-java", 
                 "Coursera", 6, "Intermediate", "Duke University Java course", 4.7, "Free"),
                
                # JavaScript
                ("JavaScript", "The Complete JavaScript Course", "https://www.udemy.com/course/the-complete-javascript-course/", 
                 "Udemy", 6, "All Levels", "Modern JavaScript from beginner to advanced", 4.7, "$19.99"),
                ("JavaScript", "JavaScript Tutorial", "https://www.youtube.com/watch?v=PkZNo7MFNFg", 
                 "YouTube", 1, "Beginner", "JavaScript full course", 4.8, "Free"),
                
                # React
                ("React", "React - The Complete Guide", "https://www.udemy.com/course/react-the-complete-guide/", 
                 "Udemy", 5, "Intermediate", "Master React including Hooks", 4.6, "$24.99"),
                ("React", "React Tutorial", "https://www.youtube.com/watch?v=Ke90Tje7VS0", 
                 "YouTube", 1, "Beginner", "React JS crash course", 4.7, "Free"),
                
                # Docker
                ("Docker", "Docker Mastery", "https://www.udemy.com/course/docker-mastery/", 
                 "Udemy", 4, "Intermediate", "Complete Docker course", 4.7, "$19.99"),
                ("Docker", "Docker Tutorial for Beginners", "https://www.youtube.com/watch?v=fqMOX6JJhGo", 
                 "YouTube", 1, "Beginner", "Docker crash course", 4.8, "Free"),
                
                # Kubernetes
                ("Kubernetes", "Kubernetes for Absolute Beginners", "https://www.udemy.com/course/learn-kubernetes/", 
                 "Udemy", 3, "Beginner", "Learn Kubernetes basics", 4.5, "$19.99"),
                ("Kubernetes", "Kubernetes Tutorial", "https://www.youtube.com/watch?v=X48VuDVv0do", 
                 "YouTube", 1, "Beginner", "Kubernetes crash course", 4.7, "Free"),
                
                # AWS
                ("AWS", "AWS Certified Solutions Architect", "https://www.udemy.com/course/aws-certified-solutions-architect-associate/", 
                 "Udemy", 12, "Intermediate", "Complete AWS certification prep", 4.7, "$24.99"),
                ("AWS", "AWS Tutorial for Beginners", "https://www.youtube.com/watch?v=k1RI5locZE4", 
                 "YouTube", 1, "Beginner", "AWS full course", 4.6, "Free"),
                
                # SQL
                ("SQL", "The Complete SQL Bootcamp", "https://www.udemy.com/course/the-complete-sql-bootcamp/", 
                 "Udemy", 3, "Beginner", "Master SQL queries", 4.6, "$19.99"),
                ("SQL", "SQL Tutorial", "https://www.youtube.com/watch?v=HXV3zeQKqGY", 
                 "YouTube", 1, "Beginner", "SQL full course", 4.7, "Free"),
                
                # MongoDB
                ("MongoDB", "MongoDB - The Complete Developer's Guide", "https://www.udemy.com/course/mongodb-the-complete-developers-guide/", 
                 "Udemy", 4, "Intermediate", "Master MongoDB", 4.6, "$19.99"),
                ("MongoDB", "MongoDB Crash Course", "https://www.youtube.com/watch?v=-56x56UppqQ", 
                 "YouTube", 1, "Beginner", "MongoDB tutorial", 4.7, "Free"),
                
                # Machine Learning
                ("Machine Learning", "Machine Learning A-Z", "https://www.udemy.com/course/machinelearning/", 
                 "Udemy", 8, "Intermediate", "Hands-on Python & R", 4.5, "$24.99"),
                ("Machine Learning", "Machine Learning by Stanford", "https://www.coursera.org/learn/machine-learning", 
                 "Coursera", 11, "Intermediate", "Andrew Ng's famous course", 4.9, "Free"),
                
                # TensorFlow
                ("TensorFlow", "TensorFlow Developer Certificate", "https://www.udemy.com/course/tensorflow-developer-certificate/", 
                 "Udemy", 6, "Intermediate", "Official TensorFlow cert prep", 4.7, "$24.99"),
                ("TensorFlow", "TensorFlow Tutorial", "https://www.youtube.com/watch?v=tPYj3fFJGjk", 
                 "YouTube", 1, "Beginner", "TensorFlow crash course", 4.6, "Free"),
                
                # Node.js
                ("Node.js", "The Complete Node.js Developer Course", "https://www.udemy.com/course/the-complete-nodejs-developer-course/", 
                 "Udemy", 5, "Intermediate", "Build real-world apps", 4.6, "$19.99"),
                ("Node.js", "Node.js Tutorial", "https://www.youtube.com/watch?v=TlB_eWDSMt4", 
                 "YouTube", 1, "Beginner", "Node.js full course", 4.7, "Free"),
                
                # TypeScript
                ("TypeScript", "Understanding TypeScript", "https://www.udemy.com/course/understanding-typescript/", 
                 "Udemy", 4, "Intermediate", "Master TypeScript", 4.7, "$19.99"),
                ("TypeScript", "TypeScript Tutorial", "https://www.youtube.com/watch?v=BwuLxPH8IDs", 
                 "YouTube", 1, "Beginner", "TypeScript crash course", 4.6, "Free"),
                
                # Git
                ("Git", "Git Complete Guide", "https://www.udemy.com/course/git-complete/", 
                 "Udemy", 2, "Beginner", "Master Git and GitHub", 4.7, "$19.99"),
                ("Git", "Git Tutorial for Beginners", "https://www.youtube.com/watch?v=8JJ101D3knE", 
                 "YouTube", 1, "Beginner", "Git crash course", 4.8, "Free"),
                
                # Redis
                ("Redis", "Redis: The Complete Developer's Guide", "https://www.udemy.com/course/redis-the-complete-developers-guide/", 
                 "Udemy", 3, "Intermediate", "Master Redis", 4.6, "$19.99"),
                
                # GraphQL
                ("GraphQL", "GraphQL with React", "https://www.udemy.com/course/graphql-with-react-course/", 
                 "Udemy", 4, "Intermediate", "Build modern APIs", 4.5, "$19.99"),
                
                # Django
                ("Django", "Django for Beginners", "https://www.udemy.com/course/django-for-beginners/", 
                 "Udemy", 5, "Beginner", "Python web framework", 4.6, "$19.99"),
                
                # Flask
                ("Flask", "REST APIs with Flask", "https://www.udemy.com/course/rest-api-flask-and-python/", 
                 "Udemy", 3, "Intermediate", "Build REST APIs", 4.6, "$19.99"),
                
                # Spring Boot
                ("Spring Boot", "Spring Boot Master Class", "https://www.udemy.com/course/spring-boot-tutorial/", 
                 "Udemy", 6, "Intermediate", "Complete Spring Boot", 4.5, "$24.99"),
            ]
            
            # Insert resources
            cursor.executemany("""
                INSERT INTO learning_resources 
                (skill_name, resource_title, resource_url, platform, duration_weeks, 
                 difficulty_level, description, rating, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, resources)
            
            self._connection.commit()
            logger.info(f"Inserted {len(resources)} sample learning resources")
            
        except sqlite3.Error as e:
            logger.error(f"Error inserting sample resources: {e}")
            # Don't raise - this is not critical
    
    def get_learning_resources_by_skill(
        self, 
        skill_name: str, 
        limit: int = 5
    ) -> List[sqlite3.Row]:
        """
        Get learning resources for a specific skill.
        
        Args:
            skill_name: Name of the skill
            limit: Maximum number of resources to return
            
        Returns:
            List of resource records
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute("""
                SELECT * FROM learning_resources 
                WHERE LOWER(skill_name) = LOWER(?)
                ORDER BY rating DESC
                LIMIT ?
            """, (skill_name, limit))
            
            resources = cursor.fetchall()
            logger.info(f"Found {len(resources)} resources for skill: {skill_name}")
            return resources
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching resources for skill {skill_name}: {e}")
            return []
    
    def save_analysis_history(
        self,
        resume_filename: str,
        user_name: Optional[str],
        user_email: Optional[str],
        extracted_skills: str,
        missing_skills: str,
        match_percentage: float,
        jobs_analyzed: int,
        cluster_id: Optional[int] = None,
        jobs_in_same_cluster: int = 0
    ) -> int:
        """
        Save analysis history to database.
        
        Returns:
            ID of inserted record
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute("""
                INSERT INTO analysis_history 
                (resume_filename, user_name, user_email, extracted_skills, missing_skills,
                 match_percentage, jobs_analyzed, cluster_id, jobs_in_same_cluster)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (resume_filename, user_name, user_email, extracted_skills, missing_skills,
                  match_percentage, jobs_analyzed, cluster_id, jobs_in_same_cluster))
            
            self._connection.commit()
            analysis_id = cursor.lastrowid
            logger.info(f"Analysis history saved with ID: {analysis_id}")
            return analysis_id
            
        except sqlite3.Error as e:
            logger.error(f"Error saving analysis history: {e}")
            return -1
    
    def save_learning_path(
        self,
        analysis_id: int,
        week_number: int,
        skill_focus: str,
        resources: str,
        milestones: str
    ) -> bool:
        """
        Save learning path for a specific week.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute("""
                INSERT INTO learning_paths 
                (analysis_id, week_number, skill_focus, resources, milestones)
                VALUES (?, ?, ?, ?, ?)
            """, (analysis_id, week_number, skill_focus, resources, milestones))
            
            self._connection.commit()
            logger.info(f"Learning path saved for analysis {analysis_id}, week {week_number}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving learning path: {e}")
            return False
    
    def get_analysis_history(self, limit: int = 10) -> List[sqlite3.Row]:
        """Get recent analysis history"""
        try:
            cursor = self._connection.cursor()
            cursor.execute("""
                SELECT * FROM analysis_history 
                ORDER BY analysis_date DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching analysis history: {e}")
            return []
    
    def clear_all_data(self) -> bool:
        """Clear all data from all tables (for testing/reset)"""
        try:
            cursor = self._connection.cursor()
            cursor.execute("DELETE FROM learning_paths")
            cursor.execute("DELETE FROM analysis_history")
            cursor.execute("DELETE FROM skills_master")
            cursor.execute("DELETE FROM learning_resources")
            self._connection.commit()
            logger.warning("All database data cleared")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing data: {e}")
            return False


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/database_manager.log", rotation="10 MB")
    
    print("=" * 60)
    print("DATABASE MANAGER TEST")
    print("=" * 60)
    
    # Test singleton pattern
    print("\n1. Testing Singleton pattern...")
    db1 = DatabaseManager()
    db2 = DatabaseManager()
    print(f"db1 is db2: {db1 is db2}")  # Should be True
    
    # Test resource fetching
    print("\n2. Testing resource fetching...")
    resources = db1.get_learning_resources_by_skill("Python", limit=3)
    for res in resources:
        print(f"  - {res['resource_title']} ({res['platform']})")
    
    # Test analysis history
    print("\n3. Testing analysis history save...")
    analysis_id = db1.save_analysis_history(
        resume_filename="test_resume.pdf",
        user_name="John Doe",
        user_email="john@example.com",
        extracted_skills="Python, Java, SQL",
        missing_skills="Docker, Kubernetes",
        match_percentage=75.5,
        jobs_analyzed=50,
        cluster_id=0,
        jobs_in_same_cluster=35
    )
    print(f"  Analysis ID: {analysis_id}")
    
    # Test learning path
    print("\n4. Testing learning path save...")
    success = db1.save_learning_path(
        analysis_id=analysis_id,
        week_number=1,
        skill_focus="Docker, Kubernetes",
        resources="Docker Mastery, Kubernetes Tutorial",
        milestones="Complete Docker tutorial, Build sample project"
    )
    print(f"  Success: {success}")
    
    print("\n" + "=" * 60)
    print("Database tests completed!")
    print(f"Database location: {db1.db_path}")
    print("=" * 60)