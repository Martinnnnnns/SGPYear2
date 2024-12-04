from datetime import datetime
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
from tutorials.forms import CancellationRequestForm, ChangeBookingForm, LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, TutorAvailabilityForm
from tutorials.models import CancellationRequest, ChangeRequest, User, LessonRequest, TutorAvailability, Lesson, Invoice, Subject
from django.db.models import Q, F


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
@login_required
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
            #objects = Lesson.objects.select_related('student', 'tutor', 'language', 'subject')
            objects = Lesson.objects.all()
            print(objects[0].status)
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
    """Redner the student's profile."""
    required_role = ["student"]
    template_name = "student_profile.html"    

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
    model = Lesson
    template_name = 'lesson_detail.html'
    context_object_name = 'lesson'
    required_role = 'student'

    def get_object(self):
        return get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
    
class StudentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    required_role = ['tutor']
    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        students_queryset = User.objects.filter(
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
    lessons = cancellation_request.lessons.all()
    for lesson in lessons:
        if lesson.status in [Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]:
            lesson.status = Lesson.STATUS_CANCELED
            lesson.save()


class RequestChangeBookingsView(LoginRequiredMixin, RoleRequiredMixin, FormView):
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
        lesson.lesson_datetime = new_datetime
        lesson.status = Lesson.STATUS_RESCHEDULED
        lesson.save()
    change_request.is_processed = True
    change_request.status = ChangeRequest.STATUS_APPROVED
    change_request.save()    

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
