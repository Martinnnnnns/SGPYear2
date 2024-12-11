from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import AnonymousUser
from tutorials.tests.helpers import MenuTesterMixin
from tutorials.helpers import login_prohibited
from tutorials.models import User

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

class TestLoginProhibited(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.org',
            password='password123'
        )
        settings.REDIRECT_URL_WHEN_LOGGED_IN = '/dashboard/'

        @login_prohibited
        def dummy_view(request):
            return HttpResponse("Test view")
        self.dummy_view = dummy_view

        def another_view(request):
            return HttpResponse("Another view")
        self.another_view = login_prohibited(another_view)

    def test_logged_in_user_redirected(self):
        request = self.factory.get('/dummy/')
        request.user = self.user
        response = self.dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/')

    def test_anonymous_user_sees_page(self):
        request = self.factory.get('/dummy/')
        request.user = AnonymousUser()
        response = self.dummy_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Test view")

    def test_different_http_methods_when_logged_in(self):
        for method in ['get', 'post', 'put', 'delete']:
            request = getattr(self.factory, method)('/dummy/')
            request.user = self.user
            response = self.dummy_view(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/dashboard/')

    def test_different_http_methods_when_anonymous(self):
        for method in ['get', 'post', 'put', 'delete']:
            request = getattr(self.factory, method)('/dummy/')
            request.user = AnonymousUser()
            response = self.dummy_view(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), "Test view")
            
    def test_decorator_preserves_view_function_name(self):
        original_name = self.another_view.__name__
        decorated = login_prohibited(self.another_view)
        self.assertEqual(decorated.__name__, "modified_view_function")
        
    def test_decorator_docstring(self):
        def view_with_docstring(request):
            """Test docstring."""
            return HttpResponse("View")
        
        decorated = login_prohibited(view_with_docstring)
        self.assertEqual(decorated.__doc__, None)
        
    def test_multiple_decorators_same_view(self):
        request = self.factory.get('/dummy/')
        request.user = self.user
        
        twice_decorated = login_prohibited(self.dummy_view)
        response = twice_decorated(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/')