"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CancellationRequest, ChangeRequest, Lesson, User, ProgrammingLanguage, Subject, LessonRequest, TutorAvailability, Role
from datetime import datetime, timedelta
from django.db import models
from tutorials.constants import UserRoles

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user

class AdminAddUserForm(forms.ModelForm):
    """Form for admin to add user"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)  
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)  
        if commit:
            user.save()  
        return user

class AdminAddBookingForm(forms.ModelForm):
    """Form for admin to add a booking"""
    class Meta:
        model = Lesson
        fields = ['student', 'tutor', 'language', 'subject', 'lesson_datetime', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        student_role = Role.objects.get(name=UserRoles.STUDENT)
        tutor_role = Role.objects.get(name=UserRoles.TUTOR)
        
        self.fields['student'] = forms.ModelChoiceField(
            queryset=User.objects.filter(current_active_role=student_role),
            required=True,
            label="Student"
        )
        self.fields['tutor'] = forms.ModelChoiceField(
            queryset=User.objects.filter(current_active_role=tutor_role),
            required=True,
            label="Tutor"
        )
    def clean_student(self):
        """Confirm the student is valid"""
        student = self.cleaned_data.get('student')
        if student and student.current_active_role != 'student':
            raise ValidationError("The selected user is not a student.")
        return student

    def clean_tutor(self):
        """Confirm the tutor is valid"""
        tutor = self.cleaned_data.get('tutor')
        if tutor and tutor.current_active_role != 'tutor':
            raise ValidationError("The selected user is not a tutor.")
        return tutor

    def save(self, commit=True):
        """Save the lesson object"""
        lesson = super().save(commit=False)

        lesson.student = self.cleaned_data.get('student')
        lesson.tutor = self.cleaned_data.get('tutor')

        if commit:
            lesson.save()
        return lesson


class UserForm(forms.ModelForm):
    """Form to update user profiles."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        
class AdminUpdateUserForm(forms.ModelForm):
    """Form for admin to update a user"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'current_active_role', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['password'] = '' 
        self.fields['password'].widget = forms.PasswordInput() 

    def clean_email(self):
        """Checks the email is valid, excluding the email they previously had"""
        email = self.cleaned_data.get('email')

        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('This email is already in use by another user.')

        return email

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.exclude(name=UserRoles.ADMIN),  #Exclude "admin" from selectable roles
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select one or more roles for the user."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', "roles"]

    def clean_roles(self):
        """Ensure at least one role is selected."""
        roles = self.cleaned_data.get('roles')
        if not roles:
            raise self.add_error("You must select at least one role.")
        return roles


    def save(self, commit=True):
        """Create a new user."""
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )

        roles = self.cleaned_data.get('roles')
        user.roles.set(roles)

        if commit:
            user.save()

        return user

class LessonRequestForm(forms.Form):
    """Form for student lesson requests."""
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    TIME_CHOICES = [
        (f"{hour:02}:{minute:02}", f"{hour:02}:{minute:02}")
        for hour in range(24)
        for minute in (0, 30)
    ]
    
    start_time = forms.ChoiceField(choices=TIME_CHOICES)
    end_time = forms.ChoiceField(choices=TIME_CHOICES)
    language = forms.ModelChoiceField(queryset=ProgrammingLanguage.objects.all(), required=True)
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        lesson_date = cleaned_data.get('date')
        start_time_str = cleaned_data.get('start_time')
        end_time_str = cleaned_data.get('end_time')

        if not (lesson_date and start_time_str and end_time_str):
            return cleaned_data

        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')
        start_datetime = datetime.combine(lesson_date, start_time.time())
        end_datetime = datetime.combine(lesson_date, end_time.time())

        if start_datetime >= end_datetime:
            raise ValidationError("End time must be after start time.")

        cleaned_data['start_datetime'] = start_datetime
        cleaned_data['end_datetime'] = end_datetime
        return cleaned_data

class TutorAvailabilityForm(forms.ModelForm):
    """Form for tutors to set their availability."""
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    recurrence = forms.ChoiceField(
        choices=TutorAvailability.RECURRENCE_CHOICES,
        widget=forms.RadioSelect(),
        initial='none'
    )
    end_recurrence_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        help_text="Required if repeating availability"
    )

    class Meta:
        model = TutorAvailability
        fields = ['date', 'start_time', 'end_time', 'recurrence', 'end_recurrence_date']

    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        recurrence = cleaned_data.get('recurrence')
        end_recurrence_date = cleaned_data.get('end_recurrence_date')

        if date and start_time and end_time:
            if date < timezone.now().date():
                self.add_error('date', "Cannot set availability for past dates")

            if end_time <= start_time:
                self.add_error('end_time', "End time must be after start time")

            if recurrence != 'none':
                if not end_recurrence_date:
                    self.add_error('end_recurrence_date', "End date is required for recurring availability")
                elif end_recurrence_date < date:
                    self.add_error('end_recurrence_date', "End date must be after start date")

            if self.tutor:
                # Check for overlapping slots
                current_date = date
                while current_date <= (end_recurrence_date or date):
                    overlapping = TutorAvailability.objects.filter(
                        tutor=self.tutor,
                        date=current_date
                    ).filter(
                        models.Q(start_time__lt=end_time, end_time__gt=start_time)
                    )
                    
                    if overlapping.exists():
                        self.add_error('start_time', f"Time slot overlaps with existing availability on {current_date}")
                        self.add_error('end_time', f"Time slot overlaps with existing availability on {current_date}")
                        break

                    if recurrence == 'weekly':
                        current_date += timedelta(days=7)
                    elif recurrence == 'biweekly':
                        current_date += timedelta(days=14)
                    else:
                        break

        return cleaned_data
    
    
class CancellationRequestForm(forms.ModelForm):
    """form for the cancellation request"""
    lessons = forms.ModelMultipleChoiceField(
        queryset=Lesson.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Lesson"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Reason for Cancellation"
    )

    class Meta:
        model = CancellationRequest
        fields = ['lessons', 'reason']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        valid_statuses = [Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]
        self.fields['lessons'].queryset = Lesson.objects.filter(
            models.Q(student=user) | models.Q(tutor=user),
            status__in=valid_statuses
        )
        
        
        
        
class ChangeRequestForm(forms.ModelForm):
    """form for changing"""
    REQUEST_SINGLE = 'single'
    REQUEST_ALL = 'all'
    REQUEST_TYPE_CHOICES = [
        (REQUEST_SINGLE, 'Single Booking'),
        (REQUEST_ALL, 'All Bookings'),
    ]

    request_type = forms.ChoiceField(
        choices=REQUEST_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Change Type"
    )
    lessons = forms.ModelMultipleChoiceField(
        queryset=Lesson.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select Lessons to Change"
    )
    new_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
        help_text="Select a new date and time for the lesson."
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Reason for Change"
    )

    class Meta:
        model = ChangeRequest
        fields = ['request_type', 'lessons', 'new_datetime', 'reason']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        valid_status = [Lesson.STATUS_SCHEDULED]
        if self.user.role == User.TUTOR:
            self.fields['lessons'].queryset = Lesson.objects.filter(
                tutor=self.user,
                status__in=valid_status
            )
        elif self.user.role == User.STUDENT:
            self.fields['lessons'].queryset = Lesson.objects.filter(
                student=self.user,
                status__in=valid_status
            )

    def clean_new_datetime(self):
        new_datetime = self.cleaned_data.get('new_datetime')
        if new_datetime and new_datetime < timezone.now():
            raise forms.ValidationError("The new date and time must be in the future.")
        return new_datetime

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        lessons = cleaned_data.get('lessons')

        if request_type == self.REQUEST_SINGLE and not lessons:
            raise forms.ValidationError("Please select at least one lesson to change.")

        if request_type == self.REQUEST_ALL:
            valid_lessons = self.fields['lessons'].queryset
            if not valid_lessons.exists():
                raise forms.ValidationError("No valid lessons found to change.")
            cleaned_data['lessons'] = valid_lessons

        return cleaned_data
    
        
class ChangeBookingDetailsForm(forms.Form):
    """Form for changing booking details."""
    lesson_id = forms.IntegerField(widget=forms.HiddenInput())
    new_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
        help_text="Select a new date and time for the lesson."
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_datetime(self):
        new_datetime = self.cleaned_data.get('new_datetime')
        if new_datetime < timezone.now():
            raise forms.ValidationError("The new date and time must be in the future.")
        return new_datetime


class ChangeBookingForm(forms.Form):
    new_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        required=True,
        help_text="Select a new date and time for the lesson"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control'
        }),
        required=False,
        label="Reason for Change"
    )

    class Meta:
        model = ChangeRequest
        fields = ('request_type', 'lessons', 'new_datetime', 'reason')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user.current_active_role.name == UserRoles.TUTOR:
            self.fields['lessons'].queryset = Lesson.objects.filter(
                tutor=self.user,
                status=Lesson.STATUS_SCHEDULED
            )
        elif self.user.current_active_role.name == UserRoles.STUDENT:
            self.fields['lessons'].queryset = Lesson.objects.filter(
                student=self.user,
                status=Lesson.STATUS_SCHEDULED
            )

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        lessons = cleaned_data.get('lessons')
        new_datetime = cleaned_data.get('new_datetime')

        if request_type == self.REQUEST_SINGLE and not lessons:
            raise forms.ValidationError('Please select at least one lesson to change.')

        if request_type == self.REQUEST_ALL:
            if self.user.current_active_role.name == UserRoles.TUTOR:
                cleaned_data['lessons'] = Lesson.objects.filter(
                    tutor=self.user,
                    status=Lesson.STATUS_SCHEDULED
                )
            elif self.user.current_active_role.name == UserRoles.STUDENT:
                cleaned_data['lessons'] = Lesson.objects.filter(
                    student=self.user,
                    status=Lesson.STATUS_SCHEDULED
                )

    def clean_new_datetime(self):
        new_datetime = self.cleaned_data.get('new_datetime')
        if new_datetime and new_datetime < timezone.now():
            raise forms.ValidationError("The new date and time must be in the future.")
        return new_datetime