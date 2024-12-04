from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse
from tutorials.tests.helpers import MenuTesterMixin

class TestMenuTesterMixin(TestCase, MenuTesterMixin):
    def test_assert_menu_loop(self):
        html = []
        for url in self.menu_urls:
            html.append(f'<a href="{url}">Menu Item</a>')
        response = HttpResponse(''.join(html))
        
        self.assert_menu(response)

    def test_assert_menu_loop_partial(self):
        html = []
        for url in self.menu_urls[:2]:
            html.append(f'<a href="{url}">Menu Item</a>')
        response = HttpResponse(''.join(html))
        
        with self.assertRaises(AssertionError):
            self.assert_menu(response)