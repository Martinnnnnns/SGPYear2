from django.shortcuts import get_object_or_404
from django.urls import reverse
from tutorials.models import Lesson  # Adjust this import to where your Lesson model is defined
from django.contrib.messages import get_messages
from tutorials.models import ProgrammingLanguage, Subject

from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin

class DeleteBookingViewTests(RoleSetupTest, AdminMixin, StudentMixin):
    
    def setUp(self):
        self.setup_admin()
        self.setup_student()

        self.language = ProgrammingLanguage.objects.create(name='Python') 
        self.subject = Subject.objects.create(name='Automation', language=self.language) 

        self.lesson = Lesson.objects.create(
            tutor=self.admin_user,  
            student=self.student_user, 
            language=self.language,
            subject=self.subject,
            lesson_datetime="2024-12-06 10:00:00",
            status=Lesson.STATUS_SCHEDULED
        )

    def test_get_delete_booking_view_as_admin(self):
        """Test admin can access the booking deletion page."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_booking.html')        
        self.assertContains(response, self.lesson.subject.name)

    def test_get_delete_booking_view_as_non_admin(self):
        """Test non-admin user is redirected when trying to access the delete booking page."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)        
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_post_delete_booking_view_as_admin(self):
            """Test admin can delete a booking via POST."""
            self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
            url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
            response = self.client.post(url)
            
            try:
                self.lesson.refresh_from_db()  # Exception if the booking was deleted
                self.fail("Lesson was not deleted successfully.")
            except Lesson.DoesNotExist:
                print("Lesson successfully deleted!")  
                
            self.assertIsNotNone(Lesson.DoesNotExist)
    
    def test_post_delete_booking_view_as_non_admin(self):
        """Test non-admin user cannot delete a booking."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('access_denied'))
        self.lesson.refresh_from_db()
        self.assertIsNotNone(self.lesson)


class DeleteUserViewTests(RoleSetupTest, ):
    
    def setUp(self):
        # Create a superuser (admin)
        self.admin_user = User.objects.create_user(
            username='@admin',
            password='adminpass',
            email='admin@example.com',
            role='admin'
        )
        
        # Create a regular student user with unique email
        self.student_user = User.objects.create_user(
            username='@student',
            password='studentpass',
            email='student@example.com'
        )
        
    def post(self, request, user_id):
        """Simulate a POST request to delete a user."""
        user_to_delete = get_object_or_404(User, id=user_id)
        user_to_delete.delete()
        messages.success(request, "User was deleted successfully.")
        return redirect(reverse('admin_list', kwargs={'list_type': 'users'}))

    def test_get_delete_user_view_as_admin(self):
        """Test admin can access the user deletion page."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin
        
        # The URL to the delete user page
        url = reverse('delete_record', kwargs={'email': self.student_user.email})
        response = self.client.get(url)
        
        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'delete_record.html')
        self.assertContains(response, self.student_user.username)

    def test_get_delete_user_view_as_non_admin(self):
        """Test non-admin user is redirected when trying to access the delete user page."""
        self.client.login(username='@student', password='studentpass')  # Log in as a regular student
        
        # The URL to the delete user page
        url = reverse('delete_record', kwargs={'email': self.admin_user.email})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_post_delete_user_view_as_admin(self):
        """Test admin can delete a user via POST."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin
        
        # The URL to delete the user
        url = reverse('delete_record', kwargs={'email': self.student_user.email})
        
        # POST request to delete the user
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('admin_list', kwargs={'list_type': 'students'}))

    def test_post_delete_user_view_as_non_admin(self):
        """Test non-admin user cannot delete a user."""
        self.client.login(username='@student', password='studentpass')  # Log in as non-admin user
        
        # The URL to delete the user
        url = reverse('delete_record', kwargs={'email': self.admin_user.email})
        
        # POST request to try to delete the user
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('access_denied'))
        
        # Ensure the admin user still exists
        self.admin_user.refresh_from_db()
        self.assertIsNotNone(self.admin_user)
