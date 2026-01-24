"""
Main Application Entry Point
Job Market Analyzer - AI-Powered Career Analysis Tool
"""

import os
import sys
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime
from loguru import logger

# Configure logger
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logger.add(
    log_dir / "job_analyzer_{time}.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)

# Import models
from .models.resume import Resume
from .models.analysis_result import AnalysisResult

# Import services (relative import)
from .services.database_manager import DatabaseManager
from .services.resume_parser import ResumeParser
from .services.skill_extractor import SkillExtractor
from .services.job_fetcher import JobFetcher
from .services.skill_analyzer import SkillAnalyzer
from .services.learning_path_generator import LearningPathGenerator

# Import utilities (relative import)
from .utils.file_validator import FileValidator
from .utils.chart_generator import ChartGenerator

class JobMarketAnalyzer:
    """
    Main application class that orchestrates all services.
    Handles the complete workflow from resume upload to results generation.
    """
    
    def __init__(self):
        """Initialize the application and all services"""
        logger.info("=" * 70)
        logger.info("Job Market Analyzer - Initializing Application")
        logger.info("=" * 70)
        
        # Initialize all services
        self.database_manager = None
        self.resume_parser = None
        self.skill_extractor = None
        self.job_fetcher = None
        self.skill_analyzer = None
        self.learning_path_generator = None
        self.chart_generator = None
        
        # Application state
        self.current_resume: Optional[Resume] = None
        self.current_result: Optional[AnalysisResult] = None
        self.is_processing = False
        
        # Initialize services
        self._initialize_services()
        
        logger.info("Application initialized successfully")
    
    def _initialize_services(self) -> None:
        """Initialize all service instances"""
        try:
            logger.info("Initializing services...")
            
            # Core services
            self.database_manager = DatabaseManager()
            logger.info("✓ Database Manager initialized")
            
            self.resume_parser = ResumeParser()
            logger.info("✓ Resume Parser initialized")
            
            self.skill_extractor = SkillExtractor()
            logger.info("✓ Skill Extractor initialized")
            
            self.job_fetcher = JobFetcher()
            logger.info("✓ Job Fetcher initialized")
            
            self.skill_analyzer = SkillAnalyzer(n_clusters=3)
            logger.info("✓ Skill Analyzer initialized")
            
            self.learning_path_generator = LearningPathGenerator()
            logger.info("✓ Learning Path Generator initialized")
            
            # Utility services
            self.chart_generator = ChartGenerator()
            logger.info("✓ Chart Generator initialized")
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    def process_resume(
        self,
        file_path: str,
        job_domain: str = "Software Developer",
        num_jobs: int = 50,
        progress_callback=None
    ) -> Optional[AnalysisResult]:
        """
        Main processing pipeline for resume analysis.
        
        Args:
            file_path: Path to resume file (PDF or image)
            job_domain: Job domain to analyze against
            num_jobs: Number of jobs to fetch
            progress_callback: Function to call with progress updates
            
        Returns:
            AnalysisResult object or None if processing fails
        """
        if self.is_processing:
            logger.warning("Processing already in progress")
            return None
        
        self.is_processing = True
        
        try:
            logger.info("=" * 70)
            logger.info(f"Starting resume processing: {file_path}")
            logger.info(f"Domain: {job_domain}, Jobs to fetch: {num_jobs}")
            logger.info("=" * 70)
            
            # Step 1: Validate file
            self._update_progress(progress_callback, "📋 Validating file...", 5)
            if not self._validate_file(file_path):
                return None
            
            # Step 2: Parse resume (extract text)
            self._update_progress(progress_callback, "📖 Extracting text from resume...", 15)
            resume = self._parse_resume(file_path)
            if not resume:
                return None
            
            # Step 3: Extract skills using NLP
            self._update_progress(progress_callback, "🔍 Identifying skills using AI...", 30)
            self._extract_skills(resume)
            
            # Step 4: Fetch job postings
            self._update_progress(progress_callback, "🌐 Fetching job postings...", 45)
            jobs = self._fetch_jobs(job_domain, num_jobs)
            if not jobs:
                logger.error("No jobs fetched")
                return None
            
            # Step 5: Analyze skills with K-Means clustering
            self._update_progress(progress_callback, "🤖 Analyzing with AI (K-Means)...", 65)
            result = self._analyze_skills(resume, jobs)
            
            # Step 6: Generate learning path
            self._update_progress(progress_callback, "📚 Creating learning path...", 80)
            learning_path = self._generate_learning_path(result)
            result.learning_path = learning_path
            
            # Step 7: Save to database
            self._update_progress(progress_callback, "💾 Saving results...", 90)
            self._save_to_database(result)
            
            # Step 8: Complete
            self._update_progress(progress_callback, "✅ Analysis complete!", 100)
            
            # Store current state
            self.current_resume = resume
            self.current_result = result
            
            logger.info("=" * 70)
            logger.info("Resume processing completed successfully")
            logger.info(f"Match: {result.match_percentage}%, "
                       f"Matching: {len(result.matching_skills)}, "
                       f"Missing: {len(result.missing_skills)}")
            logger.info("=" * 70)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during resume processing: {e}")
            self._update_progress(progress_callback, f"❌ Error: {str(e)}", 0)
            return None
        
        finally:
            self.is_processing = False
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate the uploaded file"""
        if not FileValidator.is_valid_file(file_path):
            error_msg = FileValidator.get_validation_error(file_path)
            logger.error(f"File validation failed: {error_msg}")
            return False
        
        logger.info(f"File validation passed: {file_path}")
        return True
    
    def _parse_resume(self, file_path: str) -> Optional[Resume]:
        """Parse resume and extract text"""
        resume = self.resume_parser.parse_resume(file_path)
        
        if not resume:
            logger.error("Resume parsing failed")
            return None
        
        logger.info(f"Resume parsed: {len(resume.extracted_text)} characters extracted")
        return resume
    
    def _extract_skills(self, resume: Resume) -> None:
        """Extract skills from resume text"""
        skills = self.skill_extractor.extract_skills(resume.extracted_text)
        
        # Add skills to resume
        for skill in skills:
            resume.add_skill(skill)
        
        logger.info(f"Extracted {len(skills)} skills from resume")
    
    def _fetch_jobs(self, domain: str, count: int):
        """Fetch job postings"""
        jobs = self.job_fetcher.fetch_jobs(domain, count)
        logger.info(f"Fetched {len(jobs)} job postings")
        return jobs
    
    def _analyze_skills(self, resume: Resume, jobs) -> AnalysisResult:
        """Perform skill gap analysis"""
        result = self.skill_analyzer.analyze_skills(resume, jobs)
        logger.info(f"Analysis complete: {result.match_percentage}% match")
        return result
    
    def _generate_learning_path(self, result: AnalysisResult) -> str:
        """Generate personalized learning path"""
        learning_path = self.learning_path_generator.generate_learning_path(result)
        logger.info("Learning path generated")
        return learning_path
    
    def _save_to_database(self, result: AnalysisResult) -> None:
        """Save analysis results to database"""
        try:
            # Save analysis history
            analysis_id = self.database_manager.save_analysis_history(
                resume_filename=result.resume.filename,
                user_name=result.resume.user_name,
                user_email=result.resume.email,
                extracted_skills=result.get_matching_skills_as_string(),
                missing_skills=result.get_missing_skills_as_string(),
                match_percentage=result.match_percentage,
                jobs_analyzed=result.total_jobs_analyzed,
                cluster_id=result.cluster_id,
                jobs_in_same_cluster=result.jobs_in_same_cluster
            )
            
            # Save learning path
            if analysis_id > 0:
                self.learning_path_generator.save_learning_path(
                    analysis_id=analysis_id,
                    learning_path=result.learning_path,
                    result=result
                )
                logger.info(f"Results saved to database (ID: {analysis_id})")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def _update_progress(self, callback, message: str, percentage: int) -> None:
        """Update progress if callback provided"""
        if callback:
            callback(message, percentage)
        logger.info(f"Progress: {percentage}% - {message}")
    
    def export_results(self, output_path: str) -> bool:
        """
        Export analysis results to a text file.
        
        Args:
            output_path: Path to save the results
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_result:
            logger.error("No analysis results to export")
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 70 + "\n")
                f.write("JOB MARKET ANALYZER - ANALYSIS REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Resume: {self.current_result.resume.filename}\n")
                f.write(f"Jobs Analyzed: {self.current_result.total_jobs_analyzed}\n")
                f.write(f"Overall Match: {self.current_result.match_percentage}%\n\n")
                
                # Skills summary
                f.write("─" * 70 + "\n")
                f.write("SKILLS SUMMARY\n")
                f.write("─" * 70 + "\n\n")
                
                f.write(f"✓ Skills You Have ({len(self.current_result.matching_skills)}):\n")
                f.write(f"{self.current_result.get_matching_skills_as_string()}\n\n")
                
                f.write(f"✗ Skills to Learn ({len(self.current_result.missing_skills)}):\n")
                f.write(f"{self.current_result.get_missing_skills_as_string()}\n\n")
                
                # Learning path
                f.write("─" * 70 + "\n")
                f.write("LEARNING PATH\n")
                f.write("─" * 70 + "\n\n")
                f.write(self.current_result.learning_path)
                
                f.write("\n\n" + "=" * 70 + "\n")
                f.write("End of Report\n")
                f.write("=" * 70 + "\n")
            
            logger.info(f"Results exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return False
    
    def generate_charts(self, output_dir: str = None) -> dict:
        """
        Generate all charts for the current analysis.
        
        Args:
            output_dir: Directory to save charts (optional)
            
        Returns:
            Dictionary of chart figures
        """
        if not self.current_result:
            logger.error("No analysis results to visualize")
            return {}
        
        try:
            charts = {}
            
            # Chart 1: Skill match bar chart
            charts['skill_match'] = self.chart_generator.create_skill_match_bar_chart(
                matching_count=len(self.current_result.matching_skills),
                missing_count=len(self.current_result.missing_skills),
                title="Skill Match Analysis"
            )
            
            # Chart 2: Top missing skills
            missing_skills_data = [
                {'name': s.name, 'frequency': s.frequency}
                for s in self.current_result.top_missing_skills
            ]
            charts['top_missing'] = self.chart_generator.create_top_missing_skills_chart(
                skills_data=missing_skills_data,
                top_n=10,
                title="Top 10 Most Demanded Missing Skills"
            )
            
            # Chart 3: Job match distribution
            job_matches = [
                job.calculate_match_percentage(self.current_result.resume.skills)
                for job in self.current_result.analyzed_jobs
            ]
            charts['job_distribution'] = self.chart_generator.create_job_match_distribution(
                job_matches=job_matches,
                title="Job Match Distribution"
            )
            
            # Save charts if output directory provided
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                for chart_name, fig in charts.items():
                    file_path = output_path / f"{chart_name}.html"
                    self.chart_generator.save_chart_as_html(fig, str(file_path))
                
                logger.info(f"Charts saved to: {output_dir}")
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return {}
    
    def get_job_specific_matches(self):
        """Get detailed match information for each job"""
        if not self.current_result:
            return []
        
        return self.skill_analyzer.get_job_specific_matches(
            self.current_result.resume,
            self.current_result.analyzed_jobs
        )
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        if self.database_manager:
            self.database_manager.close()
        logger.info("Application cleanup complete")


def main():
    """Main entry point for command-line usage"""
    print("=" * 70)
    print("JOB MARKET ANALYZER - AI-Powered Career Analysis Tool")
    print("=" * 70)
    print()
    
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <resume_file_path> [job_domain] [num_jobs]")
        print()
        print("Example:")
        print("  python main.py resume.pdf")
        print("  python main.py resume.pdf 'Data Scientist' 30")
        print()
        return
    
    # Parse arguments
    resume_path = sys.argv[1]
    job_domain = sys.argv[2] if len(sys.argv) > 2 else "Software Developer"
    num_jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    # Create analyzer
    analyzer = JobMarketAnalyzer()
    
    # Define progress callback
    def progress_callback(message, percentage):
        print(f"[{percentage:3d}%] {message}")
    
    # Process resume
    print(f"\nProcessing resume: {resume_path}")
    print(f"Job domain: {job_domain}")
    print(f"Jobs to analyze: {num_jobs}\n")
    
    result = analyzer.process_resume(
        file_path=resume_path,
        job_domain=job_domain,
        num_jobs=num_jobs,
        progress_callback=progress_callback
    )
    
    if result:
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE!")
        print("=" * 70)
        print(result.get_detailed_summary())
        
        # Export results
        output_file = "analysis_results.txt"
        if analyzer.export_results(output_file):
            print(f"\n✓ Results exported to: {output_file}")
        
        # Generate charts
        charts_dir = "charts"
        analyzer.generate_charts(charts_dir)
        print(f"✓ Charts saved to: {charts_dir}/")
        
        print("\n" + "=" * 70)
        print("LEARNING PATH")
        print("=" * 70)
        print(result.learning_path)
    else:
        print("\n❌ Analysis failed. Check logs for details.")
    
    # Cleanup
    analyzer.cleanup()


if __name__ == "__main__":
    main()