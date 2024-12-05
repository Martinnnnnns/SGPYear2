from django.urls import reverse
from django.test import TestCase
from tutorials.models import User  # Import your custom User model here
from tutorials.models import Lesson  # Adjust this import to where your Lesson model is defined
from django.contrib.messages import get_messages
from tutorials.models import ProgrammingLanguage, Subject
from django.utils import timezone

class DeleteBookingViewTests(TestCase):
    
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

        # Create a programming language object (ensure it exists for the subject)
        self.language = ProgrammingLanguage.objects.create(name='Python')  # Adjust as per your model

        # Create a subject object (it must have a language, so we link it here)
        self.subject = Subject.objects.create(name='Automation', language=self.language)  # Adjust as per your model

        # Create a lesson (booking) object for the test
        self.lesson = Lesson.objects.create(
            tutor=self.admin_user,  # Admin as tutor
            student=self.student_user,  # Student as the student
            language=self.language,
            subject=self.subject,
            lesson_datetime="2024-12-06 10:00:00",  # Adjust date accordingly
            status=Lesson.STATUS_SCHEDULED
        )

    def post(self, request, booking_id):
        print("POST method in DeleteBookingView called")  # Debug message
        booking_to_delete = get_object_or_404(Lesson, id=booking_id)
        print("Booking found:", booking_to_delete)  # Debug message
        booking_to_delete.delete()
        print("Booking deleted")  # Debug message
        messages.success(request, "Booking was deleted successfully.")
        return redirect(reverse('admin_list', kwargs={'list_type': 'bookings'}))


    def test_get_delete_booking_view_as_admin(self):
        """Test that an admin can access the booking deletion page."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin
        
        # The URL to the delete booking page
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        response = self.client.get(url)
        
        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Ensure the correct template is being used
        self.assertTemplateUsed(response, 'delete_booking.html')
        
        # Check if the lesson's details are in the context
        self.assertContains(response, self.lesson.subject.name)

    def test_get_delete_booking_view_as_non_admin(self):
        """Test that a non-admin user is redirected when trying to access the delete booking page."""
        self.client.login(username='@student', password='studentpass')  # Log in as a regular student
        
        # The URL to the delete booking page
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        response = self.client.get(url)
        
        # Check that the user is redirected (HTTP 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that the user is redirected to the access denied or another page
        # You may adjust this to the appropriate URL if access is denied
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_post_delete_booking_view_as_admin(self):
            """Test that an admin can delete a booking via POST."""
            self.client.login(username='@admin', password='adminpass')  # Log in as admin
            
            # The URL to delete the booking
            url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
            
            # POST request to delete the booking
            response = self.client.post(url)
            
            # Debugging: Check if lesson is deleted
            try:
                self.lesson.refresh_from_db()  # This should raise an exception if the booking was deleted
                self.fail("Lesson was not deleted successfully.")
            except Lesson.DoesNotExist:
                print("Lesson successfully deleted!")  # Confirmation message in the test
                
            self.assertIsNotNone(Lesson.DoesNotExist)
    
    def test_post_delete_booking_view_as_non_admin(self):
        """Test that a non-admin user cannot delete a booking."""
        self.client.login(username='@student', password='studentpass')  # Log in as non-admin user
        
        # The URL to delete the booking
        url = reverse('delete_booking', kwargs={'booking_id': self.lesson.id})
        
        # POST request to try to delete the booking
        response = self.client.post(url)
        
        # Ensure the user is redirected or an error is displayed (adjust accordingly)
        self.assertRedirects(response, reverse('access_denied'))
        
        # Ensure the booking still exists
        self.lesson.refresh_from_db()
        self.assertIsNotNone(self.lesson)


class DeleteUserViewTests(TestCase):
    
    def setUp(self):
        # Create a superuser (admin)
        self.admin_user = User.objects.create_user(
            username='@admin',
            password='adminpass',
            email='admin@example.com',
            role='admin'  # Assuming your User model has a 'role' field
        )
        
        # Create a regular student user with unique email
        self.student_user = User.objects.create_user(
            username='@student',
            password='studentpass',
            email='student@example.com'
        )
        
    def post(self, request, user_id):
        """Simulate a POST request to delete a user."""
        print("POST method in DeleteUserView called")  # Debug message
        user_to_delete = get_object_or_404(User, id=user_id)
        print("User found:", user_to_delete)  # Debug message
        user_to_delete.delete()
        print("User deleted")  # Debug message
        messages.success(request, "User was deleted successfully.")
        return redirect(reverse('admin_list', kwargs={'list_type': 'users'}))

    def test_get_delete_user_view_as_admin(self):
        """Test that an admin can access the user deletion page."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin
        
        # The URL to the delete user page
        url = reverse('delete_record', kwargs={'email': self.student_user.email})
        response = self.client.get(url)
        
        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Ensure the correct template is being used
        self.assertTemplateUsed(response, 'delete_record.html')
        
        # Check if the user's details are in the context
        self.assertContains(response, self.student_user.username)

    def test_get_delete_user_view_as_non_admin(self):
        """Test that a non-admin user is redirected when trying to access the delete user page."""
        self.client.login(username='@student', password='studentpass')  # Log in as a regular student
        
        # The URL to the delete user page
        url = reverse('delete_record', kwargs={'email': self.admin_user.email})
        response = self.client.get(url)
        
        # Check that the user is redirected (HTTP 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that the user is redirected to the access denied or another page
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_post_delete_user_view_as_admin(self):
        """Test that an admin can delete a user via POST."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin
        
        # The URL to delete the user
        url = reverse('delete_record', kwargs={'email': self.student_user.email})
        
        # POST request to delete the user
        response = self.client.post(url)
        
        # Debugging: Check if user is deleted
        with self.assertRaises(User.DoesNotExist):
            self.student_user.refresh_from_db()  # This should raise an exception if the user was deleted
        
        # Ensure the admin is redirected to the user list page
        self.assertRedirects(response, reverse('admin_list', kwargs={'list_type': 'students'}))
        print("User successfully deleted!")

    def test_post_delete_user_view_as_non_admin(self):
        """Test that a non-admin user cannot delete a user."""
        self.client.login(username='@student', password='studentpass')  # Log in as non-admin user
        
        # The URL to delete the user
        url = reverse('delete_record', kwargs={'email': self.admin_user.email})
        
        # POST request to try to delete the user
        response = self.client.post(url)
        
        # Ensure the user is redirected or an error is displayed
        self.assertRedirects(response, reverse('access_denied'))
        
        # Ensure the admin user still exists
        self.admin_user.refresh_from_db()
        self.assertIsNotNone(self.admin_user)
