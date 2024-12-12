from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from tutorials.models import Lesson 
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
            lesson_datetime=timezone.make_aware(datetime.strptime("2024-12-06 10:00:00", "%Y-%m-%d %H:%M:%S")),
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
        response = self.client.get(url, follow=True)
        
        self.assertEqual(response.status_code, 200)
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

