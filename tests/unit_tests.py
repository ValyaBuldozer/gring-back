import datetime
import unittest
from app import app, db
import json
from random import randint


def get_generated_name():
    rand = str(randint(1, 100000))
    return 'TestUser_' + rand


def get_generated_title():
    return "title " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M")


def get_generated_text():
    return "text " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M")


class TestHelper(unittest.TestCase):

    username = ''

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TEST_DATABASE_URI']
        with app.app_context():
            self.app = app.test_client()
            db.create_all()

    def tearDown(self):
        pass

    def generate_username(self):
        self.__class__.username = get_generated_name()

    def register(self, username, email, password):
        return self.app.put('api/user', data=json.dumps(dict(username=username, email=email,
                                                             password=password)),
                            content_type='application/json', follow_redirects=True)

    def login(self, username, password):
        return self.app.post('api/auth', data=json.dumps(dict(username=username, password=password)),
                             content_type='application/json', follow_redirects=True)

    def logout(self):
        return self.app.delete('api/auth', follow_redirects=True)

    def add_city(self, name, image_link, description):
        return self.app.put(f'api/cities',
                            data=json.dumps(dict(name=name, image_link=image_link, description=description)),
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_city_with_data(self):
        title = get_generated_title()
        text = get_generated_text()
        return self.add_city(title, "image", text)

    def add_category(self, name, label):
        return self.app.put(f'api/categories',
                            data=json.dumps(dict(name=name, label=label)),
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_category_with_data(self):
        title = get_generated_title()
        return self.add_category(title, title)

    def add_route(self, route_data):
        return self.app.put('api/routes',
                            data=route_data,
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_place(self, place_data):
        return self.app.put('api/places',
                            data=place_data,
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_place_with_data(self):
        title = get_generated_title()
        text = get_generated_text()
        place_data = json.dumps(dict(
            image_link="image",
            audioguide_link="audio",
            description=text,
            city_id=1,
            name=title,
            address="address",
            latitude=55,
            longitude=55,
            categories=[1]
        ))
        return self.add_place(place_data)

    def add_public_place(self, public_place_data):
        return self.app.put('api/public_places',
                            data=public_place_data,
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_historical_person(self, person_data):
        return self.app.put('api/historical_persons',
                            data=person_data,
                            query_string={'locale': 'en'}, content_type='application/json', follow_redirects=True)

    def add_review(self, entity_id, rating, text):
        if text is not None:
            return self.app.put(f'api/reviews/{entity_id}',
                                data=json.dumps(dict(rating=rating, text=text)),
                                content_type='application/json', follow_redirects=True)
        else:
            return self.app.put(f'api/reviews/{entity_id}',
                                data=json.dumps(dict(rating=rating)),
                                content_type='application/json', follow_redirects=True)

    def update_review(self, entity_id, rating, text):
        if text is not None:
            return self.app.post(f'api/reviews/{entity_id}',
                                 data=json.dumps(dict(rating=rating, text=text)),
                                 content_type='application/json', follow_redirects=True)
        else:
            return self.app.post(f'api/reviews/{entity_id}',
                                 data=json.dumps(dict(rating=rating)),
                                 content_type='application/json', follow_redirects=True)

    def delete_review(self, entity_id):
        return self.app.delete(f'api/reviews/{entity_id}')

    def add_favorite(self, entity_id):
        return self.app.post(f'api/user/favorites', data=json.dumps(dict(entity_id=entity_id)),
                             content_type='application/json', follow_redirects=True)

    def delete_favorite(self, entity_id):
        return self.app.delete(f'api/user/favorites/{entity_id}')

    def add_visited(self, place_id):
        return self.app.post(f'api/user/visited', data=json.dumps(dict(place_id=place_id)),
                             content_type='application/json', follow_redirects=True)

    def delete_visited(self, place_id):
        return self.app.delete(f'api/user/visited/{place_id}')


class GetTestCase(TestHelper):
    def test_get_cities(self):
        response = self.app.get('/api/cities')
        self.assertEqual(response.status_code, 200)

    def test_get_categories(self):
        response = self.app.get('/api/categories')
        self.assertEqual(response.status_code, 200)

    def test_get_routes(self):
        response = self.app.get('/api/routes')
        self.assertEqual(response.status_code, 200)

    def test_get_objects(self):
        response = self.app.get('/api/objects')
        self.assertEqual(response.status_code, 200)

    def test_get_reviews(self):
        response = self.app.get('/api/reviews')
        self.assertEqual(response.status_code, 200)


class AdminPutTestCase(TestHelper):
    def test_put_cities(self):
        title = get_generated_title()
        text = get_generated_text()
        response = self.add_city(title, "image", text)
        self.assertEqual(response.status_code, 200)

    def test_put_categories(self):
        title = get_generated_title()
        response = self.add_category(title, title)
        self.assertEqual(response.status_code, 200)

    def test_put_route(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_city_with_data()
        self.assertEqual(response.status_code, 200)

        title = get_generated_title()
        text = get_generated_text()
        route_data = json.dumps(dict(
            name=title,
            description=text,
            places=[
                {
                    "id": 1,
                    "description": "in route " + text,
                    "audioguide": "audioguide"
                }
            ],
            city_id=1
        ))
        response = self.add_route(route_data)
        self.assertEqual(response.status_code, 200)

    def test_put_place(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_city_with_data()
        self.assertEqual(response.status_code, 200)
        response = self.add_category_with_data()
        self.assertEqual(response.status_code, 200)

        title = get_generated_title()
        text = get_generated_text()
        place_data = json.dumps(dict(
            image_link="image",
            audioguide_link="audio",
            description=text,
            city_id=1,
            name=title,
            address="address",
            latitude=55,
            longitude=55,
            categories=[1]
        ))
        response = self.add_place(place_data)
        self.assertEqual(response.status_code, 200)

    def test_put_public_place(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_city_with_data()
        self.assertEqual(response.status_code, 200)
        response = self.add_category_with_data()
        self.assertEqual(response.status_code, 200)

        title = get_generated_title()
        text = get_generated_text()
        public_place_data = json.dumps(dict(
            image_link="image",
            audioguide_link="audio",
            description=text,
            city_id=1,
            name=title,
            address="address",
            latitude=55,
            longitude=55,
            categories=[1],
            timetable=[
                {
                    "day": 1,
                    "open_time": "11:00",
                    "close_time": "15:00"
                },
                {
                    "day": 2,
                    "open_time": "11:00",
                    "close_time": "14:00"
                },
            ],
            phone_number="88005553535",
            avg_bill="1000 rubles"
        ))
        response = self.add_public_place(public_place_data)
        self.assertEqual(response.status_code, 200)

    def test_put_history_person(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_city_with_data()
        self.assertEqual(response.status_code, 200)
        response = self.add_category_with_data()
        self.assertEqual(response.status_code, 200)
        for i in range(2):
            response = self.add_place_with_data()
            self.assertEqual(response.status_code, 200)

        title = get_generated_title()
        text = get_generated_text()
        person_data = json.dumps(dict(
            image_link="image",
            audioguide_link="audio",
            description=text,
            city_id=1,
            name=title,
            second_name="second_name",
            birthdate="1990-01-01",
            categories=[1],
            related_objects=[1, 2]
        ))
        response = self.add_historical_person(person_data)
        self.assertEqual(response.status_code, 200)


class UserTestCase(TestHelper):

    def test_basic_register_new_user(self):
        self.generate_username()
        response = self.register(self.__class__.username, self.__class__.username + '@mail.ru', '123')
        self.assertEqual(response.status_code, 200)

    def test_login_logout(self):
        response = self.login(self.__class__.username, '123')
        self.assertEqual(response.status_code, 200)
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        response = self.login('_' + self.__class__.username + '_', '123')
        assert b'User not found' in response.data
        response = self.login(self.__class__.username, '_123_')
        assert b'Invalid password' in response.data

    def test_reviews(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        for i in range(2):
            response = self.add_place_with_data()
            self.assertEqual(response.status_code, 200)

        rating = randint(1, 5)
        self.login(self.__class__.username, '123')
        text = get_generated_text()
        response = self.add_review(1, rating, text)
        self.assertEqual(response.status_code, 200)
        response = self.add_review(1, rating, text)
        self.assertEqual(response.status_code, 400)
        response = self.add_review(2, rating, None)
        self.assertEqual(response.status_code, 200)
        rating = randint(1, 5)
        response = self.update_review(2, rating, text)
        self.assertEqual(response.status_code, 200)
        response = self.delete_review(1)
        self.assertEqual(response.status_code, 200)
        response = self.delete_review(2)
        self.assertEqual(response.status_code, 200)

    def test_favorites(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_place_with_data()
        self.assertEqual(response.status_code, 200)

        self.login(self.__class__.username, '123')
        response = self.add_favorite(1)
        self.assertEqual(response.status_code, 200)
        response = self.add_favorite(1)
        self.assertEqual(response.status_code, 409)
        response = self.delete_favorite(1)
        self.assertEqual(response.status_code, 200)

    def test_visited_places(self):
        response = self.login('User1', '123')
        self.assertEqual(response.status_code, 200)
        response = self.add_place_with_data()
        self.assertEqual(response.status_code, 200)

        self.login(self.__class__.username, '123')
        response = self.add_visited(1)
        self.assertEqual(response.status_code, 200)
        response = self.add_visited(1)
        self.assertEqual(response.status_code, 409)
        response = self.delete_visited(1)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
        unittest.main()

