"""
Job Fetcher Service
Fetches job postings from Adzuna API or creates intelligent sample jobs
"""

import os
from typing import List, Optional
import requests
from loguru import logger

from ..models.job import Job
from ..models.skill import Skill


class JobFetcher:
    """
    Fetches job postings from external APIs or generates sample jobs.
    Primary: Adzuna API
    Fallback: Domain-specific sample jobs
    """

    ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    ADZUNA_COUNTRY = "us"

    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.api_key = os.getenv("ADZUNA_API_KEY", "")

        if not self.app_id or not self.api_key:
            logger.warning("Adzuna API credentials not found. Using sample jobs.")
        else:
            logger.info("Adzuna API credentials loaded")

    def fetch_jobs(self, query: str, count: int = 50) -> List[Job]:
        if self.app_id and self.api_key:
            try:
                jobs = self._fetch_from_api(query, count)
                if jobs:
                    return jobs
            except Exception as e:
                logger.error(f"API fetch failed: {e}")

        return self._create_sample_jobs(query, count)

    def _fetch_from_api(self, query: str, count: int) -> List[Job]:
        jobs = []
        page_size = 50
        pages_needed = (count + page_size - 1) // page_size

        for page in range(1, pages_needed + 1):
            url = (
                f"{self.ADZUNA_BASE_URL}/{self.ADZUNA_COUNTRY}/search/{page}"
                f"?app_id={self.app_id}&app_key={self.api_key}"
                f"&results_per_page={page_size}&what={query}"
            )

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            results = response.json().get("results", [])
            for job_data in results:
                job = self._parse_api_job(job_data)
                if job:
                    jobs.append(job)
                if len(jobs) >= count:
                    break

        return jobs[:count]

    def _parse_api_job(self, job_data: dict) -> Optional[Job]:
        try:
            job = Job(
                title=job_data.get("title", "Unknown"),
                company=job_data.get("company", {}).get("display_name", "Unknown"),
                description=job_data.get("description", ""),
                location=job_data.get("location", {}).get("display_name", ""),
                salary=None,
                url=job_data.get("redirect_url", ""),
                posted_date=job_data.get("created", "")
            )

            for skill in self._extract_skills_from_description(job.description):
                job.add_required_skill(skill)

            return job

        except Exception as e:
            logger.error(f"Error parsing job: {e}")
            return None

    def _extract_skills_from_description(self, description: str) -> List[Skill]:
        keywords = [
            "python", "java", "javascript", "react", "node.js", "django",
            "flask", "sql", "aws", "docker", "kubernetes", "git"
        ]

        skills = []
        desc = description.lower()
        for kw in keywords:
            if kw in desc:
                skills.append(Skill(name=kw.title(), category="Technical"))
        return skills

    def _create_sample_jobs(self, domain: str, count: int) -> List[Job]:
        domain = domain.lower()
        if "data" in domain:
            return self._create_data_scientist_jobs(count)
        if "devops" in domain:
            return self._create_devops_jobs(count)
        if "web" in domain:
            return self._create_web_developer_jobs(count)
        return self._create_software_developer_jobs(count)

    def _create_software_developer_jobs(self, count: int) -> List[Job]:
        templates = [
            ("Senior Software Engineer", "Tech Corp", ["Python", "Java", "Docker"]),
            ("Python Developer", "Data Systems", ["Python", "Django", "PostgreSQL"]),
        ]

        jobs = []
        for i in range(count):
            title, company, skills = templates[i % len(templates)]
            job = Job(
                title=title,
                company=company,
                description=f"We are hiring a {title}.",
                location="USA",
                salary="$100k+",
                url="https://example.com/job"
            )
            for s in skills:
                job.add_required_skill(Skill(name=s, category="Technical"))
            jobs.append(job)
        return jobs

    def _create_data_scientist_jobs(self, count: int) -> List[Job]:
        templates = [
            ("Data Scientist", "AI Labs", ["Python", "ML", "TensorFlow"]),
        ]

        jobs = []
        for i in range(count):
            title, company, skills = templates[i % len(templates)]
            job = Job(title=title, company=company, description="", location="USA")
            for s in skills:
                job.add_required_skill(Skill(name=s, category="Technical"))
            jobs.append(job)
        return jobs

    def _create_web_developer_jobs(self, count: int) -> List[Job]:
        templates = [
            ("Frontend Developer", "Web Studio", ["JavaScript", "React"]),
        ]

        jobs = []
        for i in range(count):
            title, company, skills = templates[i % len(templates)]
            job = Job(title=title, company=company, description="", location="Remote")
            for s in skills:
                job.add_required_skill(Skill(name=s, category="Technical"))
            jobs.append(job)
        return jobs

    def _create_devops_jobs(self, count: int) -> List[Job]:
        templates = [
            ("DevOps Engineer", "Cloud Inc", ["Docker", "Kubernetes", "AWS"]),
        ]

        jobs = []
        for i in range(count):
            title, company, skills = templates[i % len(templates)]
            job = Job(title=title, company=company, description="", location="USA")
            for s in skills:
                job.add_required_skill(Skill(name=s, category="Technical"))
            jobs.append(job)
        return jobs


if __name__ == "__main__":
    fetcher = JobFetcher()
    jobs = fetcher.fetch_jobs("Software Developer", 5)
    for job in jobs:
        print(job.title, "-", job.company)
