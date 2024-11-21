from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from tutorials.models import User
from .models import User,Lesson,Invoice
from django.core.paginator import Paginator

from .models import User

from django.core.paginator import Paginator


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


def student_dashboard(request):
    lessons = Lesson.objects.filter(student=request.user)
    invoices = Invoice.objects.filter(student=request.user)  
    return render(request, 'student_dashboard.html', {'lessons': lessons , 'invoices':invoices})
def request_lesson(request):
    return render(request,'request_lesson.html')
def student_profile(request):
    return render(request,'student_profile.html')
def student_support(request):
    return render(request,'student_support.html')
def download_invoice(request,invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, student=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.id}.pdf"'
    response.write("the amount paid is this number")  
    return response

def student_support(request):
    faqs = [
        {"question": "How do I reset my password?", "answer": "Go to the login page and click 'Forgot Password'."},
        {"question": "How do I contact my instructor?", "answer": "Navigate to the Lessons section and click on the instructor's name."},
        {"question": "What are the system requirements?", "answer": "The platform works best on modern web browsers like Chrome or Firefox."}
    ]
    return render(request, 'student_support.html', {'faqs': faqs})

def profile(request):
    return render(request, 'student_profile.html')
    

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
        return reverse('dashboard')


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
        #return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        return self.success_url