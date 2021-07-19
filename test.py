import unittest
import os
from flask.globals import current_app
from src import db, create_app


class Test(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_file='config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        with self.app_context:
            db.create_all()

    def tearDown(self) -> None:
        with self.app_context:
            db.drop_all()
        self.app_context.pop()
        os.unlink('test.db')

    def test_currentapp(self):
        self.assertNotEqual(current_app, None)

    def test_testingenv(self):
        self.assertEqual(current_app.config['ENV'], 'testing')

    def test_usercreation(self):
        response = self.client.get('/users/authenticate/register')
        self.assertEqual(response.status_code, 200)
        us = self.client.post('/users/authenticate/register', data={
            "name": "lumuliken",
            "email": "lumulikenreagan@gmail.com",
            "password": "1234",
            "twitter": "keneagan",
            "facebook": "kenreagan",
            "phone": 254710850362
        })
        self.assertEqual(us.status_code, 302)

    def test_successslogin(self):
        truelogin = self.client.post('/users/authenticate/login', data={
            "email": "lumulikenreagan@gmail.com",
            "password": "1234"
        })
        self.assertEqual(truelogin.status_code, 302)

    def test_falselogin(self):
        falselogin = self.client.post('/users/authenticate/login', data={
            "email": "lumulikenreagan@gmail.com",
            "password": "32tr784r"
        })
        self.assertTrue(
            "wrong password ensure that you enter the correct credentials",
            falselogin.get_data(as_text=True))
        self.assertEqual(falselogin.status_code, 302)

    def test_productadd(self):
        response = self.client.get('/users/add/product')
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(
            'you need to login to access this route',
            response.get_data(as_text=True))

    def test_homepage(self):
        response = self.client.get('/users/home')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
