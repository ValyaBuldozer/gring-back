import datetime
from random import randint
from locust import HttpUser, TaskSet, task, between
import gevent


class FlowException(Exception):
    pass


class GringApi(TaskSet):
    def get_objects(self):
        self.client.get("/api/objects")

    def get_object(self, object_id):
        self.client.get(f"/api/objects/{object_id}", name="/api/objects/[id]")

    def get_reviews(self, entity_id):
        self.client.get(f"/api/reviews?object={entity_id}", name="/api/reviews/[id]")

    def add_review(self, entity_id):
        rating = randint(1, 5)
        text = "test " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        data = {
            "rating": rating,
            "text": text
        }
        return self.client.put(f"/api/reviews/{entity_id}", json=data, name="/api/reviews/[id]")

    def delete_review(self, entity_id):
        self.client.delete(f"/api/reviews/{entity_id}", name="/api/reviews/[id]")

    def login(self, username):
        self.client.post("/api/auth", json={"username": username, "password": "123"})


class UnregisteredUserBehavior(GringApi):
    @task(1)
    def view_object(self):
        item_id = randint(1, 23)
        self.get_object(item_id)
        self.get_reviews(item_id)

    @task(2)
    def view_objects(self):
        self.get_objects()

    def on_start(self):
        self.get_objects()


class NormalUserBehavior(GringApi):
    @task(1)
    def add_then_delete_review(self):
        gevent.sleep(5)
        item_id = randint(1, 23)
        response = self.add_review(item_id)
        if response.status_code is not 200:
            raise FlowException("Review is not added")
        self.delete_review(item_id)

    @task(5)
    def view_object(self):
        item_id = randint(1, 23)
        self.get_object(item_id)
        self.get_reviews(item_id)

    @task(10)
    def view_objects(self):
        self.get_objects()

    def on_start(self):
        item_id = randint(1, 5)
        username = "test" + str(item_id)
        self.login(username)
        self.get_objects()


class ActiveUserBehavior(GringApi):
    @task(1)
    def add_then_delete_review(self):
        gevent.sleep(5)
        item_id = randint(1, 23)
        response = self.add_review(item_id)
        if response.status_code is not 200:
            raise FlowException("Review is not added")
        self.delete_review(item_id)

    @task(2)
    def view_object(self):
        item_id = randint(1, 23)
        self.get_object(item_id)
        self.get_reviews(item_id)

    @task(3)
    def view_objects(self):
        self.get_objects()

    def on_start(self):
        item_id = randint(1, 5)
        username = "test" + str(item_id)
        self.login(username)
        self.get_objects()


class UnregisteredUserLocust(HttpUser):
    weight = 10
    wait_time = between(5, 9)
    tasks = [UnregisteredUserBehavior]


class NormalUserLocust(HttpUser):
    weight = 5
    wait_time = between(5, 9)
    tasks = [NormalUserBehavior]


class ActiveUserLocust(HttpUser):
    weight = 1
    wait_time = between(5, 9)
    tasks = [ActiveUserBehavior]


