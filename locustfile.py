from locust import HttpUser, task, between
import random


class GraphQLUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        username = f"loadtest_{random.randint(1000, 9999)}"
        payload = {
            "query": f"""
            mutation {{
              register(username: "{username}", email: "{username}@test.com", password: "testpass123") {{
                token
              }}
            }}
            """
        }
        res = self.client.post("/graphql/", json=payload)
        try:
            token = res.json()["data"]["register"]["token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        except Exception:
            self.headers = {}

    @task(3)
    def view_posts(self):
        self.client.post(
            "/graphql/",
            json={"query": "query { posts(page:1, perPage:10) { id content } }"},
        )

    @task(2)
    def view_post(self):
        pid = random.randint(1, 20)
        self.client.post(
            "/graphql/",
            json={"query": f'query {{ post(id: "{pid}") {{ id content }} }}'},
        )

    @task(1)
    def create_post(self):
        # build content separately to avoid overly long single line
        content_text = f"load test {random.randint(1, 99999)}"
        query = (
            "mutation { createPost(content: \"" + content_text + "\") { post { id } } }"
        )
        self.client.post(
            "/graphql/",
            headers=self.headers,
            json={"query": query},
        )
