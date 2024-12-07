from datetime import datetime, timedelta
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth import login, logout, get_user_model
from datetime import datetime
from itertools import count
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import ListView, TemplateView, DetailView
from django.urls import reverse
from django.utils import timezone
import calendar
from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from tutorials.forms import CancellationRequestForm, ChangeBookingForm, LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, TutorAvailabilityForm, UpdateForm, AdminAddUserForm, AdminAddBookingForm
from tutorials.models import CancellationRequest, ChangeRequest, User, LessonRequest, TutorAvailability, Lesson, Invoice, Subject, ProgrammingLanguage
from django.db.models import Q, F
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

from tutorials.forms import CancellationRequestForm, ChangeBookingForm, LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, TutorAvailabilityForm
from tutorials.models import CancellationRequest, ChangeRequest, User, LessonRequest, TutorAvailability, Lesson, Invoice, ProgrammingLanguage

User = get_user_model()

from tutorials.models import CancellationRequest, ChangeRequest, User, LessonRequest, TutorAvailability, Lesson, Invoice
from django.db.models import Count, Case, When, IntegerField,Q



class RoleRequiredMixin:
    required_role = []  #Set this in views that use the mixin

    def dispatch(self, request, *args, **kwargs):
        if self.required_role and request.user.role not in self.required_role:
            return redirect('access_denied')  # Redirect to an access denied page
        return super().dispatch(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, View):
    """Display the appropriate dashboard based on the user's role."""
    
    def get(self, request, *args, **kwargs):
        role_dispatch = {
            'admin': self.render_admin_dashboard,
            'tutor': self.render_tutor_dashboard,
            'student': self.render_student_dashboard,
        }
        
        handler = role_dispatch.get(request.user.role, self.redirect_to_login)
        return handler(request)

    def render_admin_dashboard(self, request):
        """Render admin dashboard."""
        return render(request, 'admin_dashboard.html')

    def render_tutor_dashboard(self, request):
        """Render tutor dashboard."""
        return render(request, 'tutor_page.html', {'user': request.user})

    def render_student_dashboard(self, request):
        """Render student dashboard."""
        user = request.user
        desired_statuses = [Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        lessons = Lesson.objects.filter(
            student=user,
            status__in=desired_statuses
        ).order_by('lesson_datetime')
        invoices = Invoice.objects.filter(student=user)
        lesson_requests = user.lesson_request.filter(status='pending')
        return render(request, 'student_dashboard.html',
            {'lessons': lessons, 'invoices': invoices, 'lesson_requests': lesson_requests})

    def redirect_to_login(self, request):
        """Redirect to login if no valid role is found."""
        return redirect(reverse('log_in'))
from django.core.paginator import Paginator
from datetime import timedelta

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

""" <---- Tutor Views ----> """

class ReportsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'reports.html'
    required_role = ['tutor', 'admin']   
    

class TutorLessonsView(LoginRequiredMixin, TemplateView):
    template_name = "tutor_lessons.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lessons"] = Lesson.objects.filter(tutor=self.request.user).order_by("lesson_datetime")
        return context    

""" <---- Admin Views ----> """
class AdminViewProfile(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['admin']
    template_name = 'student_profile.html'

    def get(self, request, email):
        """Renders the confirmation page for deleting a booking."""
        userToFetch = get_object_or_404(User, email=email)
        return render(request, 'student_profile.html', {'user': userToFetch})

class AddRecordView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['admin']

    def get(self, request, role):
        """Displays form for new record, with the role based on the URL."""
        if role == 'booking':
            form = AdminAddBookingForm()
        else:
            form = AdminAddUserForm()
            
        return render(request, 'add_record.html', {'form': form, 'role': role})

    def post(self, request, role):
        """Handles form submission and creates the new user with the assigned role."""
        if role == 'booking':
            form = AdminAddBookingForm(request.POST)
        else:
            form = AdminAddUserForm(request.POST)
                    
        if form.is_valid():
            new_record = form.save(commit=False)
            
            if role != 'booking': 
                new_record.set_password(form.cleaned_data['password'])
                new_record.role = role  # Set the role to the one passed in the URL
            
            new_record.save()

            # Success message
            messages.success(request, f"{role.capitalize()} created successfully.")
            
            # Redirect to the appropriate list page
            if role == 'student':
                return redirect('admin_list', list_type='students')
            elif role == 'tutor':
                return redirect('admin_list', list_type='tutors')
            else:
                return redirect('admin_list', list_type='bookings')
            
            if role == 'booking':
                form = AdminAddBookingForm() 
            else:
                form = AdminAddUserForm()
            
        return render(request, 'add_record.html', {'form': form, 'role': role})

class AdminReviewRequestsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "admin_review_requests.html"
    required_role = ['admin']

    def get_context_data(self, **kwargs):
        """Provide context for pending requests."""
        context = super().get_context_data(**kwargs)
        context["pending_cancellations"] = CancellationRequest.objects.filter(
        status=CancellationRequest.STATUS_PENDING,
        request_type__in=[CancellationRequest.REQUEST_SINGLE, CancellationRequest.REQUEST_ALL]
    )
        context["pending_changes"] = ChangeRequest.objects.filter(status=ChangeRequest.STATUS_PENDING)
        return context

    def post(self, request, *args, **kwargs):
        """Handle approval or rejection of requests."""
        request_id = request.POST.get("request_id")
        request_type = request.POST.get("request_type")  # 'cancellation' or 'change'
        action = request.POST.get("action")  # 'approve' or 'reject'
        admin_comment = request.POST.get("admin_comment", "")

        if request_type == "cancellation":
            request_obj = get_object_or_404(CancellationRequest, id=request_id)
            if action == "approve":
                request_obj.process_approval()
                messages.success(request, "Cancellation request approved successfully.")
            elif action == "reject":
                request_obj.process_rejection()
                messages.success(request, "Cancellation request rejected successfully.")

        elif request_type == "change":
            request_obj = get_object_or_404(ChangeRequest, id=request_id)
            if action == "approve":
                if request_obj.is_within_tutor_availability():
                    request_obj.process_approval()
                    messages.success(request, "Change request approved successfully.")
                else:
                    messages.error(request, "New datetime does not align with tutor availability.")
                    return redirect("admin_review_requests")
            elif action == "reject":
                request_obj.status = ChangeRequest.STATUS_DENIED
                request_obj.save()
                messages.success(request, "Change request rejected successfully.")

        # Save admin comment
        request_obj.admin_comment = admin_comment
        request_obj.save()

        return redirect("admin_review_requests")
    
class DeleteBookingView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['admin']
    template_name = 'delete_booking.html'

    def get(self, request, booking_id):
        """Renders the confirmation page for deleting a booking."""
        booking_to_delete = get_object_or_404(Lesson, id=booking_id)

        return render(request, self.template_name, {'booking': booking_to_delete})

    def post(self, request, booking_id):
        """Deletes the booking after confirmation."""
        booking_to_delete = get_object_or_404(Lesson, id=booking_id)
        booking_to_delete.delete()

        try:
            booking_to_delete.refresh_from_db()  # Trying to access the object after deletion
        except Lesson.DoesNotExist:
            print("Booking successfully deleted!")

        messages.success(request, f"Booking was deleted successfully.")
        return redirect(reverse('admin_list', kwargs={'list_type': 'bookings'}))


class DeleteRecordView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['admin']
    template_name = 'delete_record.html'
    
    def get(self, request, email):
        """Renders the confirmation page."""
        user_to_delete = get_object_or_404(User, email=email)
        
        # Render the confirmation template
        return render(request, 'delete_record.html', {
            'user': user_to_delete,
        })

    def post(self, request, email):
        """Deletes after the admin has confirmed."""
        user_to_delete = get_object_or_404(User, email=email)
        
        user_to_delete.delete()
        
        # Success message
        messages.success(request, f"The user {user_to_delete.email} was deleted successfully.")
        
        # Redirect back to the list of users (students, tutors, etc.)
        return redirect(reverse('admin_list', kwargs={'list_type': 'students'}))  

class UpdateRecordView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    required_role = ['admin']
    model = User
    template_name = 'update_record.html'
    form_class = UpdateForm

    def get_object(self):
        # Get the user being updated
        user_id = self.kwargs.get('email') 
        return get_object_or_404(User, email=user_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        if form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(self.request, "User updated successfully!")
        return super().form_valid(form) 

    def form_invalid(self, form):
        context = self.get_context_data(form=form)  
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('dashboard')  
        

class AdminListView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['admin']

    def get(self, request, list_type):
        if request.user.role != 'admin':
            return render(request, 'home.html')

        if list_type == 'students':
            objects = User.objects.filter(role=User.STUDENT)
            page_heading = "Students"
            add_button_text = "Add Student"
            table_headers = ["Username", "Name", "Email"]
            table_fields = ['username', 'first_name', 'email']

        elif list_type == 'tutors':
            objects = User.objects.filter(role=User.TUTOR)
            page_heading = "Tutors"
            add_button_text = "Add Tutor"
            table_headers = ["Username", "Name", "Email", "Programming Language", "Subject"]
            table_fields = ['username', 'first_name', 'email', 'tutorprofile__language__name', 'tutorprofile__subject__name']

        elif list_type == 'bookings':
            objects = Lesson.objects.all()
            page_heading = "Bookings"
            add_button_text = "Add Booking"
            table_headers = ["Student", "Tutor", "Programming Language", "Subject", "Date", "Status"]
            table_fields = ['student', 'tutor', 'language', 'subject', 'lesson_datetime', 'status']

        else:
            return render(request, '404.html')  

        paginator = Paginator(objects, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Convert the QuerySet to a list of dictionaries with the required fields
        rows = []
        for obj in page_obj:
            row = {field: getattr(obj, field, '') for field in table_fields}
            rows.append(row)

        context = {
            'page_obj': page_obj,
            'page_heading': page_heading,
            'add_button_text': add_button_text,
            'table_headers': table_headers,
            'table_fields': table_fields,
            'rows': rows,
            'list_type' : list_type
        }

        return render(request, 'admin_list.html', context)

class AdminStatsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'admin_stats.html'
    required_role = ['admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_counts_by_role = User.objects.values('role').annotate(count=Count('id')).order_by('-count')
        
        subjects = Subject.objects.select_related('language').all()
        language_subject_statistics = []

        # Creates a dictionary for each subject
        for subject in subjects:
            language_subject_statistics.append({
                'language': subject.language.name,
                'subject': subject.name,
                'description': subject.description or 'No description available',
            })
            
            total_lessons = Lesson.objects.count()

        # SQL queries for table data
        lessons_per_tutor = Lesson.objects.values('tutor__first_name').annotate(lesson_count=Count('id')).order_by('-lesson_count')[:10]
        lessons_per_student = Lesson.objects.values('student__first_name').annotate(lesson_count=Count('id')).order_by('-lesson_count')[:10]

        most_popular_languages = Lesson.objects.values('language__name').annotate(language_count=Count('id')).order_by('-language_count')
        most_popular_subjects = Lesson.objects.values('subject__name').annotate(subject_count=Count('id')).order_by('-subject_count')

        context = {
            'total_lessons': total_lessons,
            'lessons_per_tutor': lessons_per_tutor,
            'lessons_per_student': lessons_per_student,
            'most_popular_languages': most_popular_languages,
            'most_popular_subjects': most_popular_subjects,
            'user_counts_by_role': user_counts_by_role,
            'language_subject_statistics': language_subject_statistics,
        }
        
        return context
    
class TriggerMatchingView(LoginRequiredMixin, RoleRequiredMixin, View):
    """An automated button to match a Student with a Lesson Request with the first avalaible tutor"""
    required_role = ['admin']
    def get(self, request):
        lesson_requests = LessonRequest.objects.filter(
            start_datetime__gte=now(), status='pending'
        )
        return render(request, 'trigger_matching.html', {
            'lesson_requests': lesson_requests,
        })
    def post(self, request):
        lesson_requests = LessonRequest.objects.filter(
            start_datetime__gte=now(), status='pending'
        )
        matched_lessons = []
        unmatched_requests = []
        for lesson_request in lesson_requests:
            busy_tutors = Lesson.objects.filter(
                lesson_datetime=lesson_request.start_datetime
            ).values_list('tutor', flat=True)
            free_tutors = User.objects.filter(
                role='tutor'
            ).exclude(id__in=busy_tutors)
            if free_tutors.exists():
                tutor = free_tutors.first()
                lesson = Lesson.objects.create(
                    student=lesson_request.user,
                    tutor=tutor,
                    lesson_datetime=lesson_request.start_datetime,
                    language=lesson_request.language,
                    subject=lesson_request.subject,
                    status=Lesson.STATUS_SCHEDULED, 
                )
                lesson_request.status = 'allocated'
                lesson_request.save()
                matched_lessons.append(lesson)
            else:
                unmatched_requests.append(lesson_request)
        return render(request, 'trigger_matching.html', {
            'matched_lessons': matched_lessons,
            'unmatched_requests': unmatched_requests,
        })
        
class TutorAvailabilityListView(LoginRequiredMixin, ListView):
    """View for Admins to see how much are the tutors booked with thier distinct colors."""
    template_name = "tutor_availability_list.html"
    context_object_name = "tutors"

    def get_queryset(self):
        queryset = User.objects.filter(role="tutor").annotate(
            scheduled_lessons=Count("lessons_as_tutor", filter=Q(lessons_as_tutor__status=Lesson.STATUS_SCHEDULED))
        )

        for tutor in queryset:
            if tutor.scheduled_lessons < 5:
                tutor.color = "green"
            elif 5 <= tutor.scheduled_lessons < 10:
                tutor.color = "yellow"
            else:
                tutor.color = "red"

        return queryset
""" <---- Student Views ----> """

class MakeLessonRequestView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    """View for students to request lessons."""
    template_name = 'make_lesson_request.html'
    form_class = LessonRequestForm
    required_role = ["student"]

    def form_valid(self, form: LessonRequestForm):
        """Process the form data and save the lesson request."""
        student = self.request.user
        lesson_request = LessonRequest(
                user=student,
                start_datetime=form.cleaned_data["start_datetime"],
                end_datetime=form.cleaned_data["end_datetime"],
                language=form.cleaned_data["language"],
                subject=form.cleaned_data["subject"])
        try:
            lesson_request.clean()  
            lesson_request.save()  
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        else:
            return super().form_valid(form)
    
    def get_form_kwargs(self):
        """Pass additional arguments to the form if needed."""
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def get_success_url(self):
        return reverse('request_made')


class LessonMadeView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """View to handle page post successful lesso request."""
    required_role = ["student"]
    template_name = "make_another_request.html"

class AccessDeniedView(TemplateView):
    """Access denied page for access to a page of an incorrect role."""
    template_name="access_denied.html"

class StudentProfileView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    required_role = ["student"]
    template_name = "student_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["programming_languages"] = user.lessons_as_student.values_list('language__name', flat=True).distinct()
        context["upcoming_lessons"] = user.lessons_as_student.filter(
            lesson_datetime__gt=timezone.now()
        ).order_by("lesson_datetime")
        context["previous_lessons"] = user.lessons_as_student.filter(
            lesson_datetime__lte=timezone.now()
        ).order_by("-lesson_datetime")
        return context
   

class StudentSupportView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """Render the student support page."""
    required_role = ["student"]
    template_name = "student_support.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faqs'] = [
            {"question": "How do I reset my password?", "answer": "Go to the login page and click 'Forgot Password'."},
            {"question": "How do I contact my instructor?", "answer": "Navigate to the Lessons section and click on the instructor's name."},
            {"question": "What are the system requirements?", "answer": "The platform works best on modern web browsers like Chrome or Firefox."}
        ]
        return context

@login_required  
def download_invoice(request,invoice_id):
    """Download invoices - NOT FUNCTIONAL YET."""
    invoice = get_object_or_404(Invoice, id=invoice_id, student=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.id}.pdf"'
    response.write("the amount paid is this number")  
    return response
    

class LessonDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    """A view to get the Lesson Details"""
    model = Lesson
    template_name = 'lesson_detail.html'
    context_object_name = 'lesson'
    required_role = 'student'

    def get_object(self):
        return get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
    
class StudentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """A view for the toutor to see his Students."""
    template_name = 'student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    required_role = ['tutor']
    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        students_queryset = User.STUDENT.objects.filter(
            role='student',
            lessons_as_student__tutor=self.request.user
        ).distinct().order_by('last_name', 'first_name')
        if search_query:
            students_queryset = students_queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        return students_queryset    
    
    
    
    
class RequestCancelBookingsView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    """A view to Cancel a Booking"""
    template_name = 'request_cancel_bookings.html'
    form_class = CancellationRequestForm
    required_role = ['student', 'tutor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        cancellation_request = form.save(commit=False)
        cancellation_request.user = self.request.user
        cancellation_request.status = ChangeRequest.STATUS_PENDING  

        cancellation_request.save()

        valid_statuses = [Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        if form.cleaned_data['request_type'] == CancellationRequest.REQUEST_SINGLE:
            lessons = form.cleaned_data['lessons'].filter(status__in=valid_statuses)
            cancellation_request.lessons.set(lessons)
        else:
            if self.request.user.role == User.TUTOR:
                lessons = Lesson.objects.filter(
                    tutor=self.request.user, status__in=valid_statuses
                )
            else:
                lessons = Lesson.objects.filter(
                    student=self.request.user, status__in=valid_statuses
                )
            cancellation_request.lessons.set(lessons)

        cancellation_request.save()
        process_cancellation_request(cancellation_request)
        messages.success(self.request, "Your cancellation request has been submitted.")
        return redirect('dashboard')
    
def process_cancellation_request(cancellation_request):
    """a function to check whether the lesson is in the apportipte field."""
    lessons = cancellation_request.lessons.all()
    for lesson in lessons:
        if lesson.status in [Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]:
            lesson.status = Lesson.STATUS_CANCELED
            lesson.save()


class RequestChangeBookingsView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    """A view to request the admin for the change bookings."""
    template_name = 'request_change_bookings.html'
    form_class = ChangeBookingForm
    required_role = ['student', 'tutor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        change_request = form.save(commit=False)
        change_request.user = self.request.user
        change_request.status = ChangeRequest.STATUS_PENDING
        change_request.save()
        change_request.lessons.set(form.cleaned_data['lessons'])
        change_request.save()
        process_change_request(change_request)
        messages.success(self.request, "Your change request has been submitted.")
        return redirect('dashboard')
    
def process_change_request(change_request):
    new_datetime = change_request.new_datetime
    lessons = change_request.lessons.all()

    for lesson in lessons:
        tutor_availability = TutorAvailability.objects.filter(
            tutor=lesson.tutor,
            date=new_datetime.date(),
            start_time__lte=new_datetime.time(),
            end_time__gte=new_datetime.time()
        )
        if tutor_availability.exists():
            lesson.lesson_datetime = new_datetime
            lesson.status = Lesson.STATUS_RESCHEDULED
            lesson.save()

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self): 
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next = settings.REDIRECT_URL_WHEN_LOGGED_IN  # Initialises self.next for self.render further down

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        user = form.get_user()
        if user is not None and user.is_active:
            login(request, user)
            return redirect(reverse("dashboard"))
        else:
            messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
            return self.render()
        

    def render(self):
        """Render log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

class LogoutView(View):
    """Log out the current user"""
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')

class HomeView(LoginProhibitedMixin, View):
    """Display the application's start/home screen."""

    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!") 
        return reverse("dashboard")
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        return self.request.user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse("dashboard")  


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form): 
        """come back"""
        self.object = form.save()
        login(self.request, self.object)
            
        self.success_url = reverse("dashboard")
        return super().form_valid(form)

    def get_success_url(self): 
        return self.success_url
    
    def get_redirect_when_logged_in_url(self):
        """Redirect logged-in users based on their role."""
        return reverse("dashboard")
            
class ScheduleSessionsView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'schedule_sessions.html'
    form_class = TutorAvailabilityForm
    success_url = '/schedule_sessions/'  
    login_url = '/login/' 
    
    def test_func(self):
        return self.request.user.role == 'tutor'
        
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        return redirect('home')  
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tutor'] = self.request.user
        return kwargs

    def form_valid(self, form):
        start_date = form.cleaned_data['date']
        end_recurrence_date = form.cleaned_data['end_recurrence_date']
        recurrence = form.cleaned_data['recurrence']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']

        if recurrence == 'none' or not end_recurrence_date:
            availability = TutorAvailability(
                tutor=self.request.user,
                date=start_date,
                start_time=start_time,
                end_time=end_time,
                recurrence=recurrence,
                end_recurrence_date=end_recurrence_date
            )
            availability.save()
        else:
            current_date = start_date
            while current_date <= end_recurrence_date:
                availability = TutorAvailability(
                    tutor=self.request.user,
                    date=current_date,
                    start_time=start_time,
                    end_time=end_time,
                    recurrence=recurrence,
                    end_recurrence_date=end_recurrence_date
                )
                availability.save()

                if recurrence == 'weekly':
                    current_date += timedelta(days=7)
                elif recurrence == 'biweekly':
                    current_date += timedelta(days=14)

        self.request.session['success_message'] = "Availability slot(s) added successfully"
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        success_message = self.request.session.pop('success_message', None)

        try:
            month = int(self.request.GET.get('month', now().month))
            year = int(self.request.GET.get('year', now().year))
        except ValueError:
            month = now().month
            year = now().year

        cal = calendar.monthcalendar(year, month)

        prev_month = 12 if month == 1 else month - 1
        prev_year = year - 1 if month == 1 else year
        next_month = 1 if month == 12 else month + 1
        next_year = year + 1 if month == 12 else year

        month_slots = TutorAvailability.objects.filter(
            tutor=self.request.user,
            date__year=year,
            date__month=month
        ).order_by('date', 'start_time')

        calendar_with_slots = []
        for week in cal:
            week_slots = []
            for day in week:
                if day != 0:
                    day_slots = [slot for slot in month_slots if slot.date.day == day]
                else:
                    day_slots = []
                week_slots.append({'day': day, 'slots': day_slots})
            calendar_with_slots.append(week_slots)

        context.update({
            'calendar': calendar_with_slots,
            'month_name': calendar.month_name[month],
            'year': year,
            'success_message': success_message,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'hours_range': [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in [0, 30]]
        })
        return context

class DeleteAvailabilityView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['tutor']

    def get(self, request, *args, **kwargs):
        return redirect('schedule_sessions')

    def post(self, request, slot_id):
        availability = get_object_or_404(TutorAvailability, id=slot_id, tutor=request.user)
        availability.delete()
        request.session['success_message'] = "Availability slot deleted successfully"
        return redirect('schedule_sessions')

class DeleteAllAvailabilityView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = ['tutor']

    def get(self, request, *args, **kwargs):
        return redirect('schedule_sessions')

    def post(self, request):
        TutorAvailability.objects.filter(tutor=request.user).delete()
        request.session['success_message'] = "All availability slots deleted successfully"
        return redirect('schedule_sessions')

class ConfirmDeleteAvailabilityView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'confirm_delete_availability.html'
    required_role = ['tutor']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slot'] = get_object_or_404(TutorAvailability, 
                                          id=self.kwargs['slot_id'], 
                                          tutor=self.request.user)
        return context

    def post(self, request, slot_id):
        slot = get_object_or_404(TutorAvailability, id=slot_id, tutor=request.user)
        slot.delete()
        messages.success(request, "Availability slot deleted successfully.")
        return redirect('schedule_sessions')

class ConfirmDeleteAllAvailabilitiesView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'confirm_delete_all_availabilities.html'
    required_role = ['tutor']

    def get(self, request, *args, **kwargs):
        if not TutorAvailability.objects.filter(tutor=request.user).exists():
            messages.info(request, "There are no slots to delete.")
            return redirect('schedule_sessions')
        return super().get(request, *args, **kwargs)

    def post(self, request):
        TutorAvailability.objects.filter(tutor=request.user).delete()
        messages.success(request, "All availability slots deleted successfully.")
        return redirect('schedule_sessions')

class GenerateReportView(LoginRequiredMixin, View):
    """View for generating styled tutor reports."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'tutor':
            return HttpResponse("You are not authorized to access this resource.", status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, time_period):
        today = now().date()

        if time_period == '7days':
            start_date = today - timedelta(days=7)
            period_text = "Last 7 Days"
        elif time_period == 'month':
            start_date = today.replace(day=1)
            period_text = f"Month of {today.strftime('%B %Y')}"
        elif time_period == 'all':
            start_date = None
            period_text = "All Time"
        else:
            return HttpResponse("Invalid time period.", status=400)

        lessons = Lesson.objects.filter(tutor=request.user)
        if start_date:
            lessons = lessons.filter(lesson_datetime__date__gte=start_date)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="tutor_report_{time_period}.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#303f9f')
        )

        story.append(Paragraph(f"Tutor Report", title_style))
        
        story.append(Paragraph(f"Tutor: {request.user.full_name()}", header_style))
        story.append(Paragraph(f"Period: {period_text}", header_style))
        story.append(Spacer(1, 20))

        table_data = [
            ['Date', 'Time', 'Student', 'Language', 'Status']
        ]
        
        for lesson in lessons:
            table_data.append([
                lesson.lesson_datetime.strftime('%Y-%m-%d'),
                lesson.lesson_datetime.strftime('%H:%M'),
                lesson.student.full_name(),
                lesson.language.name,
                lesson.get_status_display()
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')), 
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),   
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(table)

        story.append(Spacer(1, 30))
        story.append(Paragraph("Summary Statistics", header_style))
        
        total_lessons = lessons.count()
        completed_lessons = lessons.filter(status='completed').count()
        cancelled_lessons = lessons.filter(status='cancelled').count()
        
        stats_data = [
            ['Total Lessons', 'Completed', 'Cancelled'],
            [str(total_lessons), str(completed_lessons), str(cancelled_lessons)]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(stats_table)

        doc.build(story)
        return response

class TutorStudentsListView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'tutor_students_list.html'
    required_role = ['tutor']

class CurrentStudentsListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'current_students_list.html'
    context_object_name = 'students'
    required_role = ['tutor']

    def get_queryset(self):
        return User.objects.filter(
            lessons_as_student__tutor=self.request.user,
            lessons_as_student__lesson_datetime__gte=now(),
            lessons_as_student__status__in=[Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        ).distinct().order_by('last_name', 'first_name')
    
class PreviousStudentsListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'previous_students_list.html'
    context_object_name = 'students'
    required_role = ['tutor']

    def get_queryset(self):
        current_students = User.objects.filter(
            lessons_as_student__tutor=self.request.user,
            lessons_as_student__lesson_datetime__gte=now(),
            lessons_as_student__status__in=[Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        )
        
        return User.objects.filter(
            lessons_as_student__tutor=self.request.user,
            lessons_as_student__lesson_datetime__lt=now()
        ).exclude(
            id__in=current_students
        ).distinct().order_by('last_name', 'first_name')

class StudentProfileDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    template_name = 'student_profile_detail.html'
    model = User
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    required_role = ['tutor', 'admin']

    def get_object(self, queryset=None):
        student = get_object_or_404(User, id=self.kwargs['student_id'])
        # Check if the tutor has access to this student
        if self.request.user.role == 'tutor':
            if not Lesson.objects.filter(tutor=self.request.user, student=student).exists():
                raise Http404("Student not found")
        else:
            if not Lesson.objects.filter(student=student).exists():
                raise Http404("Student not found")      
        return student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        if self.request.user.role == 'admin':
            # Admins can see all lessons for the student, regardless of the tutor.
            context['upcoming_lessons'] = Lesson.objects.filter(
                student=student,
                lesson_datetime__gt=now()
            ).order_by('lesson_datetime')

            context['previous_lessons'] = Lesson.objects.filter(
                student=student,
                lesson_datetime__lte=now()
            ).order_by('-lesson_datetime')

        elif self.request.user.role == 'tutor':
            # Tutors can only see their own lessons with the student.
            context['upcoming_lessons'] = Lesson.objects.filter(
                tutor=self.request.user,
                student=student,
                lesson_datetime__gt=now()
            ).order_by('lesson_datetime')

            context['previous_lessons'] = Lesson.objects.filter(
                tutor=self.request.user,
                student=student,
                lesson_datetime__lte=now()
            ).order_by('-lesson_datetime')
        
        all_lessons = Lesson.objects.filter(tutor=self.request.user, student=student)
        context['programming_languages'] = all_lessons.values_list('language__name', flat=True).distinct()
        
        return context

class StudentLessonCalendarView(LoginRequiredMixin, RoleRequiredMixin, View):
    """Display student lessons in a calendar format."""
    template_name = 'student_calendar.html'
    required_role = ['student']

    def get(self, request):
        # Get current month and year from request or use current date
        current_date = timezone.now()
        month = int(request.GET.get('month', current_date.month))
        year = int(request.GET.get('year', current_date.year))

        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        
        # Get all lessons for the month for this student
        lessons = Lesson.objects.filter(
            student=request.user,
            lesson_datetime__year=year,
            lesson_datetime__month=month,
            status__in=[Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        ).order_by('lesson_datetime')

        # Create calendar with lessons
        calendar_data = []
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': 0, 'lessons': []})
                else:
                    day_lessons = [
                        lesson for lesson in lessons
                        if lesson.lesson_datetime.day == day
                    ]
                    week_data.append({
                        'day': day,
                        'lessons': day_lessons
                    })
            calendar_data.append(week_data)

        # Calculate previous and next month/year
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        context = {
            'calendar': calendar_data,
            'month_name': calendar.month_name[month],
            'year': year,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'current_month': month,
            'current_year': year
        }
        return render(request, self.template_name, context)

class StudentInvoicesView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """Display all invoices for a student."""
    template_name = 'student_invoices.html'
    required_role = ['student']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = Invoice.objects.filter(student=self.request.user)
        return context

class StudentPendingRequestsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """Display all pending lesson requests for a student."""
    template_name = 'student_pending_requests.html'
    required_role = ['student']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson_requests'] = self.request.user.lesson_request.filter(status='pending')
        return context