from sklearn.metrics.pairwise import cosine_similarity

def calculate_match(resume_emb, job_emb):
    score = cosine_similarity([resume_emb], [job_emb])[0][0]
    return round(float(score * 100), 2)