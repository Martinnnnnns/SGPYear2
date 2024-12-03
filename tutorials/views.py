from datetime import datetime
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
from tutorials.models import User, LessonRequest, TutorAvailability, Lesson, Invoice
from django.core.paginator import Paginator
from datetime import timedelta

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
def admin_dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'admin_dashboard.html')
    else:
        return render(request, 'home.html')

@login_required
def admin_student_list(request):
    if request.user.role == 'admin':
        students = User.objects.filter(role=User.STUDENT)

        # Creates a Paginator object and renders the specified page
        paginator = Paginator(students, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'admin_student_list.html', {'page_obj': page_obj})
    else:
        return render(request, 'home.html')

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

""" <---- Student Views ----> """
@login_required
def student_dashboard(request):
    """Student dashboard."""
    user = User.objects.get(pk=request.user.id)
    lessons = Lesson.objects.filter(student=request.user)
    invoices = Invoice.objects.filter(student=request.user)  
    lesson_requests = user.lesson_request.all()
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
            start_date = form.cleaned_data['date']
            end_recurrence_date = form.cleaned_data['end_recurrence_date']
            recurrence = form.cleaned_data['recurrence']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            # For one-time slots or if no end date is specified
            if recurrence == 'none' or not end_recurrence_date:
                availability = TutorAvailability(
                    tutor=request.user,
                    date=start_date,
                    start_time=start_time,
                    end_time=end_time,
                    recurrence=recurrence,
                    end_recurrence_date=end_recurrence_date
                )
                availability.save()
            else:
                # For recurring slots
                current_date = start_date
                while current_date <= end_recurrence_date:
                    availability = TutorAvailability(
                        tutor=request.user,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        recurrence=recurrence,
                        end_recurrence_date=end_recurrence_date
                    )
                    availability.save()

                    # Calculate next date based on recurrence type
                    if recurrence == 'weekly':
                        current_date += timedelta(days=7)
                    elif recurrence == 'biweekly':
                        current_date += timedelta(days=14)

            request.session['success_message'] = "Availability slot(s) added successfully"
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

    # Generate a list of hour options (00:00 to 23:30)
    hours_range = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in [0, 30]]

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
        'hours_range': hours_range,  # Pass the generated time options
    }

    return render(request, 'schedule_sessions.html', context)

@login_required
def delete_availability(request, slot_id):
    if request.user.role != 'tutor':
        return redirect('home')
        
    # Get the availability slot and check it belongs to the logged-in tutor
    availability = get_object_or_404(TutorAvailability, id=slot_id, tutor=request.user)
    
    if request.method == 'POST':
        availability.delete()
        request.session['success_message'] = "Availability slot deleted successfully"
        
    return redirect('schedule_sessions')

@login_required
def delete_all_availability(request):
    if request.user.role != 'tutor':
        return redirect('home')

    TutorAvailability.objects.filter(tutor=request.user).delete()
    request.session['success_message'] = "All availability slots deleted successfully"
    return redirect('schedule_sessions')

@login_required
def confirm_delete_availability(request, slot_id):
    slot = TutorAvailability.objects.get(id=slot_id, tutor=request.user)
    if request.method == 'POST':
        # Perform the deletion if confirmed
        slot.delete()
        messages.success(request, "Availability slot deleted successfully.")
        return redirect('schedule_sessions')
    return render(request, 'confirm_delete_availability.html', {'slot': slot})

@login_required
def confirm_delete_all_availabilities(request):
    # Check if the user has any availability slots
    availability_exists = TutorAvailability.objects.filter(tutor=request.user).exists()

    if not availability_exists:
        messages.info(request, "There are no slots to delete.")
        return redirect('schedule_sessions')

    if request.method == 'POST':
        TutorAvailability.objects.filter(tutor=request.user).delete()
        messages.success(request, "All availability slots deleted successfully.")
        return redirect('schedule_sessions') 

    return render(request, 'confirm_delete_all_availabilities.html')
