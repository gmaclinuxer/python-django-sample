#coding=utf8
from django.test import TestCase
from django.test.client import Client
from django.test import LiveServerTestCase
from selenium import webdriver


# Create your tests here.
class ChatTests(TestCase):
    client_class = Client

    def test(self):
        self.assertEqual(1 + 1, 2)

class ChatLiveTests(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)

    def test_student_find_solos(self):
        """
        Test
        """
        self.fail('Incomplete Test')

