from datetime import datetime
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from django.utils import timezone
import calendar
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, TutorAvailabilityForm
from tutorials.helpers import login_prohibited
from tutorials.models import User, LessonRequest, TutorAvailability, Lesson, Invoice, Subject
from django.core.paginator import Paginator
from django.db.models import Count, Avg


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})
@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

""" <---- Tutor Views ----> """
@login_required
def tutor_page(request):
    """Display the tutors' dashboard."""
    if request.user.role == 'tutor':
        current_user = request.user
        return render(request, 'tutor_page.html', {'user': current_user})
    else:
        return render(request, 'home.html')
    
@login_required
def schedule_sessions(request):
    if request.user.role == 'tutor':
        return render(request, 'schedule_sessions.html')
    else:
        return render(request, 'home.html')

@login_required
def reports(request):
    if request.user.role == 'tutor':
        return render(request, 'reports.html')
    elif request.user.role == 'admin':
        return render(request, 'reports.html')
    else:
        return render(request, 'home.html')

""" <---- Admin Views ----> """

@login_required
def admin_list(request, list_type):
    if request.user.role != 'admin':
        return render(request, 'home.html')

    if list_type == 'students':
        objects = User.objects.filter(role=User.STUDENT).annotate(
            username=F('username'),
            name=F('first_name'),
            email=F('email')
        )
        page_heading = "Students"
        add_button_text = "Add Student"
        table_headers = ["Username", "Name", "Email"]
        table_fields = ['username', 'name', 'email']

    elif list_type == 'tutors':
        objects = User.objects.filter(role=User.TUTOR).annotate(
            username=F('username'),
            name=F('first_name'),
            email=F('email'),
            language=F('tutorprofile__language__name'),  # Adjust based on your model relationships
            subject=F('tutorprofile__subject__name')    # Adjust as needed
        )
        page_heading = "Tutors"
        add_button_text = "Add Tutor"
        table_headers = ["Username", "Name", "Email", "Programming Language", "Subject"]
        table_fields = ['username', 'name', 'email', 'language', 'subject']

    elif list_type == 'bookings':
        objects = Lesson.objects.select_related('student', 'tutor').annotate(
            student=F('student__first_name'),
            tutor=F('tutor__first_name'),
            language=F('language__name'),
            subject=F('subject__name'),
            lesson_datetime=F('lesson_datetime')
        )
        page_heading = "Bookings"
        add_button_text = "Add Booking"
        table_headers = ["Student", "Tutor", "Programming Language", "Subject", "Date"]
        table_fields = ['student', 'tutor', 'language', 'subject', 'lesson_datetime']

    else:
        return render(request, '404.html')  # Handle invalid list_type

    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'page_heading': page_heading,
        'add_button_text': add_button_text,
        'table_headers': table_headers,
        'table_fields': table_fields,
    }

    return render(request, 'admin_list.html', context)

@login_required
def admin_dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'admin_dashboard.html')
    else:
        return render(request, 'home.html')

@login_required
def admin_list(request, list_type):
    if request.user.role != 'admin':
        return render(request, 'home.html')

    if list_type == 'students':
        objects = User.objects.filter(role=User.STUDENT)
        page_heading = "Students"
        add_button_text = "Add Student"
        table_headers = ["Username", "Name", "Email"]
        table_rows = [
            [student.username, f"{student.first_name} {student.last_name}", student.email]
            for student in objects
        ]

    elif list_type == 'tutors':
        objects = User.objects.filter(role=User.TUTOR)
        page_heading = "Tutors"
        add_button_text = "Add Tutor"
        table_headers = ["Username", "Name", "Email", "Programming Language", "Subject"]
        table_rows = [
            [
                tutor.username,
                f"{tutor.first_name} {tutor.last_name}",
                tutor.email,
                "a",
                "a",
            ]
            for tutor in objects
        ]

    elif list_type == 'bookings':
        objects = Lesson.objects.select_related('student', 'tutor', 'language', 'subject')
        page_heading = "Bookings"
        add_button_text = "Add Booking"
        table_headers = ["Student", "Tutor", "Programming Language", "Subject", "Date"]
        table_rows = [
            [
                f"{booking.student.first_name} {booking.student.last_name}",
                f"{booking.tutor.first_name} {booking.tutor.last_name}",
                booking.language.name if booking.language else "N/A",
                booking.subject.name if booking.subject else "N/A",
                booking.lesson_datetime,
            ]
            for booking in objects
        ]

    else:
        return render(request, '404.html')  

    # Paginate the table_rows
    paginator = Paginator(table_rows, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'page_heading': page_heading,
        'add_button_text': add_button_text,
        'table_headers': table_headers,
    }

    return render(request, 'admin_list.html', context)


@login_required
def admin_tutor_list(request):
    if request.user.role == 'admin':
        tutors = User.objects.filter(role=User.TUTOR)
        
        # Creates a Paginator object and renders the specified page
        paginator = Paginator(tutors, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'admin_tutor_list.html', {'page_obj': page_obj})
    else:
        return render(request, 'home.html')

@login_required
def admin_bookings_list(request):
    if request.user.role == 'admin':
        #bookings = User.objects.all()
        bookings = Lesson.objects.all()

        # Creates a Paginator object and renders the specified page
        paginator = Paginator(bookings, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'admin_bookings_list.html', {'page_obj': page_obj})
    else:
        return render(request, 'home.html')
    
@login_required
def admin_stats(request):
    if request.user.role == 'admin':
        
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
        
        return render(request, 'admin_stats.html', context)
    else:
        return render(request, 'home.html')
    
@login_required
def trigger_matching(request):
    if request.user.role != 'admin':
        return render(request, '403.html', status=403)  # Restrict access to non-admin users

    if request.method == "GET":
        # Preview unmatched lesson requests
        lesson_requests = LessonRequest.objects.filter(start_datetime__gte=now(), status='pending')
        return render(request, 'trigger_matching.html', {
            'lesson_requests': lesson_requests,
        })

    if request.method == "POST":
        # Perform the matching logic
        lesson_requests = LessonRequest.objects.filter(start_datetime__gte=now(), status='pending')
        matched_lessons = []
        unmatched_requests = []

        for lesson_request in lesson_requests:
            busy_tutors = Lesson.objects.filter(
                lesson_datetime=lesson_request.start_datetime
            ).values_list('tutor', flat=True)
            free_tutors = User.objects.filter(role='tutor').exclude(id__in=busy_tutors)

            if free_tutors.exists():
                tutor = free_tutors.first()
                lesson = Lesson.objects.create(
                    student=lesson_request.user,
                    tutor=tutor,
                    lesson_datetime=lesson_request.start_datetime,
                    language=lesson_request.language,
                    subject=lesson_request.subject,
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

    return JsonResponse({"error": "Invalid request method."}, status=405)    

""" <---- Student Views ----> """
@login_required
def student_dashboard(request):
    """Student dashboard."""
    user = User.objects.get(pk=request.user.id)
    lessons = Lesson.objects.filter(student=request.user)
    invoices = Invoice.objects.filter(student=request.user)  
    lesson_requests = user.lesson_request.filter(status='pending')
    return render(request, 'student_dashboard.html',{'lessons': lessons , 'invoices':invoices, "lesson_requests":lesson_requests})

@login_required
def make_lesson_request(request: HttpRequest):
    """View for students to request lessons."""
    student = User.objects.get(pk=request.user.id)  #Assume logged-in user
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = LessonRequest(
                user=student,
                start_datetime=form.cleaned_data["start_datetime"],
                end_datetime=form.cleaned_data["end_datetime"],
                language=form.cleaned_data["language"],
                subject=form.cleaned_data["subject"]
            )
            try:
                lesson_request.clean()  #Model-level validation
                lesson_request.save()  #Save to the database if no validation errors
                return redirect('request_made')  
            except ValidationError as e:
                form.add_error(None, e)  
                return render(request, 'make_lesson_request.html', {'form': form})

    else:
        form = LessonRequestForm()
    return render(request, 'make_lesson_request.html', {'form': form})
print(f"LessonRequest created: {LessonRequest}")

def combine_date_and_time(date_str, time_str):
    """Helper function to combine date and time into a datetime object"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(date_obj, time_obj)
    except ValueError:
        return None

@login_required
def lesson_made(request: HttpRequest):
    """Landing page upon successful lesson request made."""
    return render(request, 'make_another_request.html')

@login_required  
def student_profile(request):
    """View student profile."""
    return render(request,'student_profile.html')

@login_required  
def student_support(request):
    """View student support page."""
    return render(request,'student_support.html')

@login_required  
def download_invoice(request,invoice_id):
    """Download invoices - NOT FUNCTIONAL YET."""
    invoice = get_object_or_404(Invoice, id=invoice_id, student=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.id}.pdf"'
    response.write("the amount paid is this number")  
    return response

@login_required  
def student_support(request):
    """View FAQ page."""
    faqs = [
        {"question": "How do I reset my password?", "answer": "Go to the login page and click 'Forgot Password'."},
        {"question": "How do I contact my instructor?", "answer": "Navigate to the Lessons section and click on the instructor's name."},
        {"question": "What are the system requirements?", "answer": "The platform works best on modern web browsers like Chrome or Firefox."}
    ]
    return render(request, 'student_support.html', {'faqs': faqs})
    
@login_required    
def lesson_detail(request, lesson_id):
    """Display individual lesson details after clicking icon on student dashboard."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'lesson_detail.html', context={"lesson": lesson})

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

        # Determine the redirect URL before checking login success
        if user is not None:
            if user.role == 'admin':
                self.next = 'admin_dashboard' 
            elif user.role == 'tutor':
                self.next = 'tutor_page' 
            elif user.role == 'student':
                self.next = 'student_dashboard'  
            else: 
                """come back"""
                self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN

            # Log the user in and redirect
            login(request, user)
            return redirect(self.next)

        # If authentication fails, show an error and re-render the form
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


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

        # Redirect based on user role
        if self.request.user.role == 'admin':
            return reverse('admin_dashboard')
        elif self.request.user.role == 'tutor':
            return reverse('tutor_page')
        elif self.request.user.role == 'student':
            return reverse('student_dashboard')
        else:
            # Default
            return reverse('home') 
            
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
        user = self.request.user

        # URL is determined by role
        if user.role == 'admin':
            redirect_url_name = 'admin_dashboard'
        elif user.role == 'tutor':
            redirect_url_name = 'tutor_page'
        elif user.role == 'student':
            redirect_url_name = 'student_dashboard'
        else:
            redirect_url_name = settings.REDIRECT_URL_WHEN_LOGGED_IN

        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(redirect_url_name)  


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form): 
        """come back"""
        self.object = form.save()
        login(self.request, self.object)
        
        # Set the redirection URL based on user role
        if self.object.role == 'admin':
            self.success_url = reverse('admin_dashboard')
        elif self.object.role == 'tutor':
            self.success_url = reverse('tutor_page')
        elif self.object.role == 'student':
            self.success_url = reverse('student_dashboard')
        else:
            # Default URL
            self.success_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            
        return super().form_valid(form)

    def get_success_url(self): 
        """come back"""
        #return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        return self.success_url
    
    def get_redirect_when_logged_in_url(self):
        """Redirect logged-in users based on their role."""
        user = self.request.user
        if user.role == 'admin':
            return reverse('admin_dashboard')
        elif user.role == 'tutor':
            return reverse('tutor_page')
        elif user.role == 'student':
            return reverse('student_dashboard')
        else:
            return super().get_redirect_when_logged_in_url() 
            """come back"""

@login_required
def schedule_sessions(request):
    if request.user.role != 'tutor':
        return redirect('home')
        
    if request.method == 'POST':
        form = TutorAvailabilityForm(request.POST, tutor=request.user)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.tutor = request.user
            availability.save()
            request.session['success_message'] = "Availability slot added successfully"
            return redirect('schedule_sessions')
    else:
        form = TutorAvailabilityForm(tutor=request.user)

    success_message = request.session.pop('success_message', None)
    
    try:
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))
    except ValueError:
        month = timezone.now().month
        year = timezone.now().year
    
    cal = calendar.monthcalendar(year, month)
    
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
    
    month_slots = TutorAvailability.objects.filter(
        tutor=request.user,
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

    context = {
        'form': form,
        'calendar': calendar_with_slots,
        'month_name': calendar.month_name[month],
        'year': year,
        'success_message': success_message,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'schedule_sessions.html', context)