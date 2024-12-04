from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse
from tutorials.tests.helpers import MenuTesterMixin
from django.conf import settings
from django.conf.urls.static import static

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

class TestStaticUrlPatterns(TestCase):
    def test_static_url_configuration(self):
        original_debug = settings.DEBUG
        original_static_url = settings.STATIC_URL
        original_static_root = settings.STATIC_ROOT

        try:
            settings.DEBUG = True
            settings.STATIC_URL = '/static/'
            settings.STATIC_ROOT = '/tmp/static'

            static_patterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
            self.assertIsNotNone(static_patterns)

        finally:
            settings.DEBUG = original_debug
            settings.STATIC_URL = original_static_url
            settings.STATIC_ROOT = original_static_root

    def test_static_settings(self):
        self.assertIsNotNone(settings.STATIC_URL)
        self.assertTrue(settings.STATIC_URL.startswith('/'))
        self.assertIsNotNone(settings.STATIC_ROOT)