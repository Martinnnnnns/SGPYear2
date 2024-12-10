from datetime import datetime, timedelta
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib.auth import login, logout, get_user_model
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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tutorials.forms import CancellationRequestForm, ChangeBookingForm, LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, TutorAvailabilityForm
from tutorials.models import CancellationRequest, ChangeRequest, User, LessonRequest, TutorAvailability, Lesson, Invoice, ProgrammingLanguage, Role
from tutorials.constants import UserRoles

User = get_user_model()
from django.db.models import Q

class RoleRequiredMixin:
    required_role = []  #Set this in views that use the mixin

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.required_role and request.user.current_active_role.name not in self.required_role:
            return redirect('access_denied')  # Redirect to an access denied page
        return super().dispatch(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, View):
    """Display the appropriate dashboard based on the user's role."""

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.current_active_role:
            return redirect(reverse("role_select"))

        role_dispatch = {
            'admin': self.render_admin_dashboard,
            'tutor': self.render_tutor_dashboard,
            'student': self.render_student_dashboard,
        }
        handler = role_dispatch.get(request.user.current_active_role.name, self.redirect_to_login)
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
    
class SetActiveRoleView(LoginRequiredMixin, TemplateView):
    """View to set the user's current active role and redirect to the dashboard."""
    template_name = "set_active_role.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        """Handle GET requests."""
        roles = request.user.roles.all()

        #Redirect if there is only one role
        if roles.count() == 1:
            request.user.current_active_role = roles.first()
            request.user.save()
            return HttpResponseRedirect(reverse("dashboard"))

        # Show the template for role selection if multiple roles exist
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Pass the user's roles to the template."""
        context = super().get_context_data(**kwargs)
        context['roles'] = self.request.user.roles.all()
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        """Handle setting the active role."""
        role = request.POST.get('role')
        if not role:
            return self.render_to_response(self.get_context_data(error="No role selected."))

        try:
            selected_role = Role.objects.get(name=role)
        except Role.DoesNotExist:
            return self.render_to_response(self.get_context_data(error="Invalid role selection."))

        request.user.current_active_role = selected_role
        request.user.save()
        return HttpResponseRedirect(reverse("dashboard"))

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
    
class AdminListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    paginate_by = 20
    required_role = ['admin']  
    model = None
    template_name = None  

    def get_queryset(self):
        return super().get_queryset()

class AdminStudentListView(AdminListView):
    model = User
    template_name = 'admin_student_list.html'
    context_object_name = 'students'

class AdminTutorListView(AdminListView):
    model = User
    template_name = 'admin_tutor_list.html'
    context_object_name = 'tutors'

class AdminBookingsListView(AdminListView):
    model = Lesson
    template_name = 'admin_bookings_list.html'
    context_object_name = 'bookings'

    
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
                roles_contain='tutor'
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

class MakeLessonRequestView(LoginRequiredMixin, FormView):
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
            if self.request.user.current_active_role.name == UserRoles.TUTOR:
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
            return redirect(reverse("role_select"))
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
        if request.user.is_authenticated:
            request.user.current_active_role = None
            request.user.save()
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

    def form_valid(self, form: SignUpForm):
        """Process the form data and save the new user."""        
        user = form.save()
        login(self.request, user)

        self.success_url = reverse("role_select")
        return super().form_valid(form)

    def get_success_url(self): 
        return self.success_url
    
    def get_redirect_when_logged_in_url(self):
        """Redirect logged-in users based on their role."""
        return reverse("role_select")
            
class ScheduleSessionsView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'schedule_sessions.html'
    form_class = TutorAvailabilityForm
    success_url = '/schedule_sessions/'  
    login_url = '/login/' 
    
    def test_func(self):
        return self.request.user.current_active_role.name == UserRoles.TUTOR
        
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
    required_role = [UserRoles.TUTOR]

    def get(self, request, *args, **kwargs):
        return redirect('schedule_sessions')

    def post(self, request, slot_id):
        availability = get_object_or_404(TutorAvailability, id=slot_id, tutor=request.user)
        availability.delete()
        request.session['success_message'] = "Availability slot deleted successfully"
        return redirect('schedule_sessions')

class DeleteAllAvailabilityView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_role = [UserRoles.TUTOR]
    def get(self, request, *args, **kwargs):
        return redirect('schedule_sessions')

    def post(self, request):
        TutorAvailability.objects.filter(tutor=request.user).delete()
        request.session['success_message'] = "All availability slots deleted successfully"
        return redirect('schedule_sessions')

class ConfirmDeleteAvailabilityView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'confirm_delete_availability.html'
    required_role = [UserRoles.TUTOR]

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
    required_role = [UserRoles.TUTOR]

    def get(self, request, *args, **kwargs):
        if not TutorAvailability.objects.filter(tutor=request.user).exists():
            messages.info(request, "There are no slots to delete.")
            return redirect('schedule_sessions')
        return super().get(request, *args, **kwargs)

    def post(self, request):
        TutorAvailability.objects.filter(tutor=request.user).delete()
        messages.success(request, "All availability slots deleted successfully.")
        return redirect('schedule_sessions')

class GenerateReportView(LoginRequiredMixin, RoleRequiredMixin, View):
    """View for generating tutor reports."""
    required_role = [UserRoles.TUTOR]

    def get(self, request, time_period):
        today = now().date()

        if time_period == '7days':
            start_date = today - timedelta(days=7)
        elif time_period == 'month':
            start_date = today.replace(day=1)
        elif time_period == 'all':
            start_date = None
        else:
            return HttpResponse("Invalid time period.", status=400)

        lessons = Lesson.objects.filter(tutor=request.user)
        if start_date:
            lessons = lessons.filter(lesson_datetime__date__gte=start_date)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="tutor_report_{time_period}.pdf"'

        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 750, f"Tutor Report for {request.user.full_name()}")
        pdf.drawString(50, 730, f"Time Period: {time_period}")

        y_position = 700
        for lesson in lessons:
            if y_position < 50:
                pdf.showPage()
                y_position = 750

            pdf.drawString(50, y_position, f"Student: {lesson.student.full_name()}")
            pdf.drawString(250, y_position, f"Date: {lesson.lesson_datetime.strftime('%Y-%m-%d %H:%M')}")
            pdf.drawString(450, y_position, f"Language: {lesson.language.name}")
            y_position -= 20

        pdf.save()
        return response

class TutorStudentsListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'tutor_students_list.html'
    context_object_name = 'students'   
    required_role = ["tutor"]

    def get_queryset(self):
        return User.objects.filter(
            lessons_as_student__tutor=self.request.user
        ).distinct()

class StudentProfileDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    template_name = 'student_profile_detail.html'
    required_role = [UserRoles.TUTOR]
    model = User
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    
    def dispatch(self, request, *args, **kwargs):
        student = self.get_object()
        if not Lesson.objects.filter(tutor=request.user, student=student).exists():
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(User, id=self.kwargs['student_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
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