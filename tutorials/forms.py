"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, ProgrammingLanguage, Subject, LessonRequest, TutorAvailability
from datetime import datetime, timedelta
from django.db import models

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


class UserForm(forms.ModelForm):
    """Form to update user profiles."""
    
    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

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
    
    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            role=self.cleaned_data.get('role'),
        )
        return user
    

class LessonRequestForm(forms.Form):
    """Form for student lesson requests."""
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    #Time fields for start and end times with manual 30-minute intervals
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

        #Add start and end datetime to cleaned_data
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

    class Meta:
        model = TutorAvailability
        fields = ['date', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if date and start_time and end_time:
            if date < timezone.now().date():
                self.add_error('date', "Cannot set availability for past dates")

            if end_time <= start_time:
                self.add_error('end_time', "End time must be after start time")

            if self.tutor:
                overlapping = TutorAvailability.objects.filter(
                    tutor=self.tutor,
                    date=date
                ).filter(
                    models.Q(start_time__lt=end_time, end_time__gt=start_time)
                )
                
                if overlapping.exists():
                    self.add_error('start_time', "This time slot overlaps with existing availability")
                    self.add_error('end_time', "This time slot overlaps with existing availability")

        return cleaned_data