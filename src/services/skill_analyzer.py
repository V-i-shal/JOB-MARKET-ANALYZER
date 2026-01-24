"""
Skill Analyzer Service
AI-powered skill gap analysis using K-Means clustering
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from loguru import logger

# Import models
from ..models.resume import Resume
from ..models.job import Job
from ..models.skill import Skill
from ..models.analysis_result import AnalysisResult


class SkillAnalyzer:
    """
    Analyzes skill gaps using K-Means clustering.
    Groups similar skill profiles (resume + jobs) into clusters,
    then calculates match based on cluster similarity.
    """
    
    def __init__(self, n_clusters: int = 3):
        """
        Initialize the skill analyzer.
        
        Args:
            n_clusters: Number of clusters for K-Means (default: 3)
                       Represents different career paths/skill profiles
        """
        self.n_clusters = n_clusters
        logger.info(f"SkillAnalyzer initialized with {n_clusters} clusters")
    
    def analyze_skills(self, resume: Resume, jobs: List[Job]) -> AnalysisResult:
        """
        Main analysis method. Performs skill gap analysis using ML clustering.
        
        Args:
            resume: User's resume object
            jobs: List of job postings to analyze against
            
        Returns:
            AnalysisResult object with complete analysis
        """
        if not jobs:
            logger.error("No jobs provided for analysis")
            return self._create_empty_result(resume)
        
        if not resume.skills:
            logger.warning("Resume has no skills extracted")
            return self._create_empty_result(resume)
        
        try:
            logger.info(f"Analyzing {len(resume.skills)} resume skills against {len(jobs)} jobs")
            
            # Create analysis result object
            result = AnalysisResult(
                resume=resume,
                analyzed_jobs=jobs
            )
            
            # Step 1: Identify skill gaps (matching vs missing)
            self._identify_skill_gaps(resume, jobs, result)
            
            # Step 2: Calculate match percentage using K-Means clustering
            try:
                match_percentage, cluster_id, jobs_in_cluster = self._calculate_match_with_clustering(
                    resume, jobs
                )
                result.match_percentage = match_percentage
                result.cluster_id = cluster_id
                result.jobs_in_same_cluster = jobs_in_cluster
                logger.info(f"K-Means clustering successful: {match_percentage}% match")
            except Exception as e:
                logger.warning(f"K-Means clustering failed: {e}. Using simple overlap.")
                result.match_percentage = self._calculate_simple_overlap(resume, jobs)
                result.cluster_id = None
                result.jobs_in_same_cluster = 0
            
            # Step 3: Sort missing skills by importance (frequency in jobs)
            result.missing_skills.sort(key=lambda s: s.frequency, reverse=True)
            
            logger.info(f"Analysis complete: {result.match_percentage}% match, "
                       f"{len(result.matching_skills)} matching, {len(result.missing_skills)} missing")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during skill analysis: {e}")
            return self._create_empty_result(resume)
    
    def _identify_skill_gaps(
        self,
        resume: Resume,
        jobs: List[Job],
        result: AnalysisResult
    ) -> None:
        """
        Identify which skills match and which are missing.
        
        Args:
            resume: User's resume
            jobs: List of jobs
            result: AnalysisResult to populate
        """
        # Collect all unique skills from all jobs
        all_job_skills: Dict[str, Skill] = {}
        
        for job in jobs:
            for skill in job.required_skills:
                skill_name_lower = skill.name.lower()
                
                if skill_name_lower not in all_job_skills:
                    # Create new skill entry
                    all_job_skills[skill_name_lower] = Skill(
                        name=skill.name,
                        category=skill.category,
                        is_technical=skill.is_technical,
                        frequency=1
                    )
                else:
                    # Increment frequency (how many jobs require this skill)
                    all_job_skills[skill_name_lower].increment_frequency()
        
        # Create set of user's skills (lowercase for comparison)
        user_skill_names = {skill.name.lower() for skill in resume.skills}
        
        # Categorize skills
        for skill_name_lower, job_skill in all_job_skills.items():
            if skill_name_lower in user_skill_names:
                # User has this skill - add to matching
                result.add_matching_skill(job_skill)
            else:
                # User doesn't have this skill - add to missing
                result.add_missing_skill(job_skill)
        
        logger.info(f"Skill gaps identified: {len(result.matching_skills)} matching, "
                   f"{len(result.missing_skills)} missing")
    
    def _calculate_match_with_clustering(
        self,
        resume: Resume,
        jobs: List[Job]
    ) -> Tuple[float, int, int]:
        """
        Calculate match percentage using K-Means clustering.
        
        Args:
            resume: User's resume
            jobs: List of jobs
            
        Returns:
            Tuple of (match_percentage, cluster_id, jobs_in_same_cluster)
        """
        # Step 1: Create master skill list
        master_skills = self._create_master_skill_list(resume, jobs)
        logger.debug(f"Master skill list: {len(master_skills)} unique skills")
        
        if len(master_skills) == 0:
            raise ValueError("No skills found for clustering")
        
        # Step 2: Create feature vectors (skill presence matrix)
        resume_vector = self._create_skill_vector(resume.skills, master_skills)
        job_vectors = [self._create_skill_vector(job.required_skills, master_skills) 
                      for job in jobs]
        
        # Combine all vectors (resume + all jobs)
        all_vectors = np.vstack([resume_vector, np.array(job_vectors)])
        
        # Step 3: Normalize features (optional but recommended)
        scaler = StandardScaler()
        all_vectors_scaled = scaler.fit_transform(all_vectors)
        
        # Step 4: Apply K-Means clustering
        n_clusters = min(self.n_clusters, len(all_vectors))  # Don't exceed data points
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        cluster_labels = kmeans.fit_predict(all_vectors_scaled)
        
        # Step 5: Determine resume's cluster
        resume_cluster = cluster_labels[0]
        
        # Step 6: Count jobs in same cluster as resume
        job_clusters = cluster_labels[1:]  # Exclude resume (first element)
        jobs_in_same_cluster = np.sum(job_clusters == resume_cluster)
        
        # Step 7: Calculate match percentage
        match_percentage = (jobs_in_same_cluster / len(jobs)) * 100
        
        logger.info(f"Clustering results: Resume in cluster {resume_cluster}, "
                   f"{jobs_in_same_cluster}/{len(jobs)} jobs in same cluster")
        
        return round(match_percentage, 2), int(resume_cluster), int(jobs_in_same_cluster)
    
    def _create_master_skill_list(self, resume: Resume, jobs: List[Job]) -> List[str]:
        """
        Create a master list of all unique skills (from resume + all jobs).
        
        Args:
            resume: User's resume
            jobs: List of jobs
            
        Returns:
            Sorted list of unique skill names (lowercase)
        """
        all_skills: Set[str] = set()
        
        # Add resume skills
        for skill in resume.skills:
            all_skills.add(skill.name.lower())
        
        # Add job skills
        for job in jobs:
            for skill in job.required_skills:
                all_skills.add(skill.name.lower())
        
        # Return sorted list for consistent ordering
        return sorted(list(all_skills))
    
    def _create_skill_vector(
        self,
        skills: List[Skill],
        master_skills: List[str]
    ) -> np.ndarray:
        """
        Create a binary feature vector for a skill set.
        Vector has 1 if skill is present, 0 if absent.
        
        Args:
            skills: List of skills to encode
            master_skills: Master list of all possible skills
            
        Returns:
            Binary numpy array of shape (len(master_skills),)
        """
        # Create set of skill names (lowercase) for O(1) lookup
        skill_names = {skill.name.lower() for skill in skills}
        
        # Create binary vector
        vector = np.zeros(len(master_skills), dtype=int)
        for i, master_skill in enumerate(master_skills):
            if master_skill in skill_names:
                vector[i] = 1
        
        return vector
    
    def _calculate_simple_overlap(self, resume: Resume, jobs: List[Job]) -> float:
        """
        Fallback method: Calculate match as simple skill overlap percentage.
        
        Args:
            resume: User's resume
            jobs: List of jobs
            
        Returns:
            Match percentage (0-100)
        """
        if not jobs:
            return 0.0
        
        # Collect all unique required skills from jobs
        all_required_skills: Set[str] = set()
        for job in jobs:
            for skill in job.required_skills:
                all_required_skills.add(skill.name.lower())
        
        if not all_required_skills:
            return 0.0
        
        # Count how many required skills user has
        user_skills = {skill.name.lower() for skill in resume.skills}
        matching_count = len(all_required_skills.intersection(user_skills))
        
        # Calculate percentage
        match_percentage = (matching_count / len(all_required_skills)) * 100
        
        return round(match_percentage, 2)
    
    def _create_empty_result(self, resume: Resume) -> AnalysisResult:
        """
        Create an empty analysis result (fallback for errors).
        
        Args:
            resume: User's resume
            
        Returns:
            Empty AnalysisResult
        """
        result = AnalysisResult(resume=resume)
        result.match_percentage = 0.0
        logger.warning("Created empty analysis result")
        return result
    
    def get_job_specific_matches(
        self,
        resume: Resume,
        jobs: List[Job]
    ) -> List[Dict[str, any]]:
        """
        Calculate match percentage for each individual job.
        
        Args:
            resume: User's resume
            jobs: List of jobs
            
        Returns:
            List of dicts with job and match info
        """
        matches = []
        
        for job in jobs:
            match_pct = job.calculate_match_percentage(resume.skills)
            matching_skills = job.get_matching_skills(resume.skills)
            missing_skills = job.get_missing_skills(resume.skills)
            
            matches.append({
                'job': job,
                'match_percentage': match_pct,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'matching_count': len(matching_skills),
                'missing_count': len(missing_skills)
            })
        
        # Sort by match percentage (highest first)
        matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return matches


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/skill_analyzer.log", rotation="10 MB")
    
    print("=" * 60)
    print("SKILL ANALYZER TEST")
    print("=" * 60)
    
    # Create sample resume
    from models.resume import Resume, FileType
    resume = Resume(filename="test_resume.pdf", file_type=FileType.PDF)
    resume.add_skill(Skill("Python", "Programming Language"))
    resume.add_skill(Skill("Java", "Programming Language"))
    resume.add_skill(Skill("SQL", "Database"))
    resume.add_skill(Skill("Git", "Version Control"))
    
    print(f"\nResume Skills: {resume.get_skills_as_string()}")
    
    # Create sample jobs
    jobs = []
    
    # Job 1: Backend Developer (similar to resume)
    job1 = Job("Backend Developer", "Tech Corp")
    job1.add_required_skill(Skill("Python", "Programming Language"))
    job1.add_required_skill(Skill("Django", "Framework"))
    job1.add_required_skill(Skill("SQL", "Database"))
    job1.add_required_skill(Skill("Docker", "DevOps"))
    jobs.append(job1)
    
    # Job 2: Java Developer (similar to resume)
    job2 = Job("Java Developer", "Enterprise Inc")
    job2.add_required_skill(Skill("Java", "Programming Language"))
    job2.add_required_skill(Skill("Spring", "Framework"))
    job2.add_required_skill(Skill("SQL", "Database"))
    job2.add_required_skill(Skill("Git", "Version Control"))
    jobs.append(job2)
    
    # Job 3: Data Scientist (different skill set)
    job3 = Job("Data Scientist", "AI Lab")
    job3.add_required_skill(Skill("Python", "Programming Language"))
    job3.add_required_skill(Skill("Machine Learning", "ML"))
    job3.add_required_skill(Skill("TensorFlow", "ML"))
    job3.add_required_skill(Skill("Pandas", "Data"))
    jobs.append(job3)
    
    print(f"\nAnalyzing against {len(jobs)} jobs...\n")
    
    # Perform analysis
    analyzer = SkillAnalyzer(n_clusters=2)
    result = analyzer.analyze_skills(resume, jobs)
    
    # Display results
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"\nOverall Match: {result.match_percentage}%")
    print(f"Cluster ID: {result.cluster_id}")
    print(f"Jobs in Same Cluster: {result.jobs_in_same_cluster}/{len(jobs)}")
    
    print(f"\n✓ Matching Skills ({len(result.matching_skills)}):")
    for skill in result.matching_skills:
        print(f"  • {skill.name} (required by {skill.frequency} jobs)")
    
    print(f"\n✗ Missing Skills ({len(result.missing_skills)}):")
    for skill in result.top_missing_skills:
        print(f"  • {skill.name} (required by {skill.frequency} jobs)")
    
    # Job-specific matches
    print("\n" + "=" * 60)
    print("JOB-SPECIFIC MATCHES")
    print("=" * 60)
    
    job_matches = analyzer.get_job_specific_matches(resume, jobs)
    for i, match in enumerate(job_matches, 1):
        print(f"\n{i}. {match['job'].title} - {match['match_percentage']}% match")
        print(f"   Matching: {match['matching_count']}, Missing: {match['missing_count']}")
    
    print("\n" + "=" * 60)
    print("Skill analyzer tests completed!")
    print("=" * 60)