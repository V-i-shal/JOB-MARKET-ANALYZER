import pandas as pd
import time
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.skill_extractor import SkillExtractor

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
CSV_PATH = r"C:\Users\visha\Downloads\archive (23)\gpt_dataset.csv"  # ← update path to your file
RESUME_COLUMN = "Resume"
NUM_RESUMES = 50  # only 3 rows in your dataset

GROUND_TRUTH_SKILLS = [
    "python", "sql", "machine learning", "pandas", "numpy",
    "scikit-learn", "data analysis", "statistics", "excel",
    "tableau", "power bi", "nlp", "deep learning", "tensorflow",
    "javascript", "react", "node", "html", "css", "java",
    "flask", "django", "docker", "git", "aws"
]

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=[RESUME_COLUMN])
resumes = df[RESUME_COLUMN].head(NUM_RESUMES).tolist()
categories = df["Category"].head(NUM_RESUMES).tolist()
print(f"Loaded {len(resumes)} resumes\n")

# ─────────────────────────────────────────
# INITIALIZE
# ─────────────────────────────────────────
skill_extractor = SkillExtractor()

# ─────────────────────────────────────────
# BATCH RUN
# ─────────────────────────────────────────
all_extracted_skills = []
processing_times = []
precision_scores = []
recall_scores = []
f1_scores = []

print("Running skill extraction...")
print("-" * 60)

for i, (resume_text, category) in enumerate(zip(resumes, categories)):
    start = time.time()

    extracted = skill_extractor.extract_skills(resume_text)
    extracted_names = [
        s.name.lower() if hasattr(s, 'name') else str(s).lower()
        for s in extracted
    ]

    elapsed = time.time() - start
    processing_times.append(elapsed)
    all_extracted_skills.append(extracted_names)

    # F1 against ground truth
    y_true = [1 if skill in resume_text.lower() else 0
              for skill in GROUND_TRUTH_SKILLS]
    y_pred = [1 if skill in extracted_names else 0
              for skill in GROUND_TRUTH_SKILLS]

    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)

    precision_scores.append(p)
    recall_scores.append(r)
    f1_scores.append(f)

    print(f"Resume {i+1} [{category}]")
    print(f"  Skills extracted : {len(extracted_names)}")
    print(f"  Skills found     : {', '.join(extracted_names[:8])}{'...' if len(extracted_names) > 8 else ''}")
    print(f"  Processing time  : {elapsed:.2f}s")
    print(f"  Precision        : {p:.4f}")
    print(f"  Recall           : {r:.4f}")
    print(f"  F1-Score         : {f:.4f}")
    print()

# ─────────────────────────────────────────
# COSINE SIMILARITY
# ─────────────────────────────────────────
skill_strings = [" ".join(skills) for skills in all_extracted_skills]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(skill_strings)

mock_job = "python sql machine learning data analysis pandas scikit-learn statistics"
job_vector = vectorizer.transform([mock_job])
cosine_scores = cosine_similarity(tfidf_matrix, job_vector).flatten()
avg_cosine = cosine_scores.mean()

# ─────────────────────────────────────────
# SILHOUETTE (needs at least 2 samples and 2 clusters)
# ─────────────────────────────────────────
sil_score = None
if len(resumes) >= 3:
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(tfidf_matrix.toarray())
    sil_score = silhouette_score(tfidf_matrix.toarray(), cluster_labels)

# ─────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────
print("=" * 60)
print("BATCH EVALUATION RESULTS")
print("=" * 60)
print(f"Resumes Processed       : {len(resumes)}")
print(f"Avg Processing Time     : {sum(processing_times)/len(processing_times):.2f}s")
print("-" * 60)
print(f"Avg Precision           : {sum(precision_scores)/len(precision_scores):.4f}")
print(f"Avg Recall              : {sum(recall_scores)/len(recall_scores):.4f}")
print(f"Avg F1-Score            : {sum(f1_scores)/len(f1_scores):.4f}")
print("-" * 60)
print(f"Avg Cosine Similarity   : {avg_cosine:.4f}")
if sil_score is not None:
    print(f"Silhouette Score (K=2)  : {sil_score:.4f}")
print("=" * 60)

# Save
results_df = pd.DataFrame({
    "Category": categories,
    "Skills_Extracted": [len(s) for s in all_extracted_skills],
    "Processing_Time": processing_times,
    "Precision": precision_scores,
    "Recall": recall_scores,
    "F1_Score": f1_scores,
    "Cosine_Similarity": cosine_scores,
})
results_df.to_csv("batch_eval_results.csv", index=False)
print("\nDetailed results saved to: batch_eval_results.csv")