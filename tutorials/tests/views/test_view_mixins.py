from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from tutorials.views import LoginProhibitedMixin

class LoginProhibitedMixinTestCase(TestCase):

    def test_login_prohibited_throws_exception_when_not_configured(self):
        """Test that an ImproperlyConfigured exception is raised when no URL is set."""
        mixin = LoginProhibitedMixin()
        with self.assertRaises(ImproperlyConfigured):
            mixin.get_redirect_when_logged_in_url()

    def test_get_redirect_when_logged_in_url_returns_student_dashboard_url(self):
        """Test that the method returns the correct student dashboard URL when set."""
        expected_url = '/student_dashboard/'
        mixin = LoginProhibitedMixin()
        mixin.redirect_when_logged_in_url = expected_url  
        
        self.assertEqual(mixin.get_redirect_when_logged_in_url(), expected_url)

    def test_get_redirect_when_logged_in_url_returns_tutor_dashboard_url(self):
        """Test that the method returns the correct tutor dashboard URL when set."""
        expected_url = '/tutor_page/'
        mixin = LoginProhibitedMixin()
        mixin.redirect_when_logged_in_url = expected_url  
        
        self.assertEqual(mixin.get_redirect_when_logged_in_url(), expected_url)

    def test_get_redirect_when_logged_in_url_returns_admin_dashboard_url(self):
        """Test that the method returns the correct admin dashboard URL when set."""
        expected_url = '/admin_dashboard/'
        mixin = LoginProhibitedMixin()
        mixin.redirect_when_logged_in_url = expected_url  
        
        self.assertEqual(mixin.get_redirect_when_logged_in_url(), expected_url)
