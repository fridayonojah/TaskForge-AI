import json
import random
from locust import HttpUser, task, between, events

TRAVEL_QUERIES = [
    "Plan a 7 days Japan trip from Bangladesh under 2 lakhs",
    "Plan a 5 days Dubai trip from Dhaka with flights and hotels",
    "Plan a 7 days Thailand trip from Bangladesh with budget hotels",
]
SLIDE_TOPICS = ["Artificial Intelligence in Healthcare", "Climate Change Solutions", "Future of Work"]
INDUSTRIES = ["Fintech", "Healthcare", "Electric Vehicles", "E-commerce"]
RESUME_TEXT = """
John Doe | john@example.com
Software Engineer with 3 years experience in Python.
- Built REST APIs using Django
- Deployed applications on AWS
- Led team of 2 developers
"""


class TaskForgeUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    @task(3)
    def plan_trip(self):
        payload = {"message": random.choice(TRAVEL_QUERIES)}
        with self.client.post("/api/travel", json=payload, catch_response=True) as resp:
            if resp.status_code == 200:
                data = resp.json()
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")

    @task(2)
    def create_slides(self):
        payload = {"topic": random.choice(SLIDE_TOPICS), "num_slides": 6}
        with self.client.post("/api/slides", json=payload, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")

    @task(2)
    def polish_resume(self):
        payload = {"resume_text": RESUME_TEXT}
        with self.client.post("/api/resume/polish", json=payload, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")

    @task(1)
    def build_sheet(self):
        payload = {"topic": "Monthly Budget Tracker", "requirements": "Track income, expenses, savings by category"}
        with self.client.post("/api/sheet", json=payload, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")

    @task(1)
    def research_industry(self):
        payload = {"industry": random.choice(INDUSTRIES)}
        with self.client.post("/api/research", json=payload, catch_response=True) as resp:
            if resp.status_code in (200, 202):
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")

    @task(1)
    def health_check(self):
        self.client.get("/api/health")
