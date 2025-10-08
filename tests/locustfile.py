import os
import random
from locust import HttpUser, task, between


class QuaggaUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Called once per user when they start - set up authentication"""
        # Set the session cookie manually (get this from your browser after logging in)
        self.client.cookies.set("session", os.getenv("SESSION_COOKIE"))

    @task(5)
    def submit_query(self):
        """Submit a query to the endpoint"""
        response = self.client.post(
            "/submit_query",
            data={
                "kg_endpoint": "https://data.gesis.org/gesiskg/sparql",
                "nl_question": "What is the capital of France?",
                "kg_name": "GESIS KG",
                "kg_description": "GESIS Social Science Knowledge Graph",
                "kg_about_page": "https://www.gesis.org/home",
                "is_dump_url": False,
            },
            name="Submit Query",
        )
        print(f"Response: {response.status_code}, Body: {response.text}")

    @task(5)
    def view_home(self):
        """View home page with statistics"""
        self.client.get("/home", name="Home Page")

    @task(3)
    def browse_all_kgs(self):
        """Browse all knowledge graphs"""
        self.client.get("/browse", name="Browse All KGs")

    @task(2)
    def browse_specific_kg(self):
        """Browse submissions for a specific KG"""
        kg_endpoints = [
            "https://data.gesis.org/gesiskg/sparql",
            "https://lux.collections.yale.edu",
        ]
        kg = random.choice(kg_endpoints)
        self.client.get(
            f"/browse/{kg}", name="Browse Specific KG"
        )

    @task(1)
    def view_faq(self):
        """View FAQ page"""
        self.client.get("/faq", name="FAQ Page")
