from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from tutorials.constants import UserRoles
from tutorials.models import Invoice, TutorAvailability, User, ProgrammingLanguage, Subject, Lesson, Role

import pytz
from faker import Faker
from random import randint, choices, choice
from datetime import datetime, time, timedelta

DEFAULT_ADMIN = {
    'username': '@johndoe',
    'email': 'john.doe@example.org',
    'first_name': 'John',
    'last_name': 'Doe',
    'roles': [UserRoles.ADMIN],
    'is_staff': True,
    'is_superuser': True,
}

DEFAULT_TUTOR = {
    'username': '@janedoe',
    'email': 'jane.doe@example.org',
    'first_name': 'Jane',
    'last_name': 'Doe',
    'roles': [UserRoles.TUTOR]
}

DEFAULT_STUDENT = {
    'username': '@charlie',
    'email': 'charlie.johnson@example.org',
    'first_name': 'Charlie',
    'last_name': 'Johnson',
    'roles': [UserRoles.STUDENT]
}
FIXED_USER_FIXTURES = (DEFAULT_ADMIN, DEFAULT_TUTOR, DEFAULT_STUDENT)

DEFAULT_LESSONS = [
    {
        'language': 'Python',
        'subject_name': 'Web Development',
        'days_from_now': -5,  
    },
    {
        'language': 'JavaScript',
        'subject_name': 'React',
        'days_from_now': -20,
    },
    {
        'language': 'Java',
        'subject_name': 'Spring Framework',
        'days_from_now': -365,
    },
    {
        'language': 'Ruby',
        'subject_name': 'Rails',
        'days_from_now': 60,
    }
]

programming_languages = [
    "Python", "JavaScript", "Java", "C++", "Ruby", "Go", "Swift", "Rust", 
    "PHP", "C#",
]

programming_topics = {
    "Python": [
        {"name": "Web Development", "description": "Building dynamic websites and web applications using frameworks like Django and Flask."},
        {"name": "Data Science", "description": "Analyzing and visualizing data using libraries like Pandas, NumPy, and Matplotlib."},
        {"name": "Machine Learning", "description": "Building machine learning models with libraries like TensorFlow, Keras, and Scikit-learn."},
        {"name": "Automation", "description": "Automating repetitive tasks using scripts and libraries like Selenium and OpenPyXL."},
        {"name": "Game Development", "description": "Creating games using libraries like Pygame or integrating with game engines like Unity."}
    ],
    "JavaScript": [
        {"name": "Frontend Development", "description": "Developing the user interface and user experience of web applications using HTML, CSS, and JavaScript."},
        {"name": "Backend Development", "description": "Creating server-side logic and databases using Node.js and Express.js."},
        {"name": "Web Frameworks", "description": "Using frameworks like React, Vue, and Angular for efficient frontend development."},
        {"name": "Node.js", "description": "Building scalable network applications with JavaScript runtime outside the browser."},
        {"name": "React", "description": "Building modern, component-based user interfaces with the React library."}
    ],
    "Java": [
        {"name": "Spring Framework", "description": "A comprehensive framework for building enterprise applications with Java."},
        {"name": "Android Development", "description": "Creating Android mobile applications using Java and Android SDK."},
        {"name": "Enterprise Applications", "description": "Building large-scale applications that handle business processes."},
        {"name": "Big Data", "description": "Working with large datasets using tools like Apache Hadoop and Apache Spark."}
    ],
    "C++": [
        {"name": "Systems Programming", "description": "Writing low-level code for operating systems, drivers, and hardware interfaces."},
        {"name": "Game Development", "description": "Creating high-performance games using game engines like Unreal Engine."},
        {"name": "Graphics Programming", "description": "Developing 2D and 3D graphics using OpenGL and DirectX."},
        {"name": "Embedded Systems", "description": "Developing software for devices with limited resources like microcontrollers."}
    ],
    "Ruby": [
        {"name": "Rails", "description": "Web development framework for building database-backed web applications."},
        {"name": "Web Development", "description": "Building dynamic websites and web applications using Ruby and frameworks like Sinatra."},
        {"name": "Automation", "description": "Automating tasks with scripts and tools like Capybara and Rake."},
        {"name": "Scripting", "description": "Writing scripts to automate or manage tasks on various systems."}
    ],
    "Go": [
        {"name": "Concurrency", "description": "Writing programs that can perform multiple tasks simultaneously using Go's goroutines."},
        {"name": "Web Development", "description": "Building web servers and APIs using Go and frameworks like Gin."},
        {"name": "Systems Programming", "description": "Developing software for operating systems, utilities, and networking tools."},
        {"name": "Microservices", "description": "Creating scalable, maintainable services using Go and a microservices architecture."}
    ],
    "Swift": [
        {"name": "iOS Development", "description": "Creating mobile applications for Apple's iOS using Swift and Xcode."},
        {"name": "macOS Development", "description": "Building desktop applications for macOS using Swift and AppKit."},
        {"name": "App Development", "description": "Building both mobile and desktop applications across Apple's ecosystem."}
    ],
    "Rust": [
        {"name": "Systems Programming", "description": "Writing systems software, including operating systems, file systems, and networking tools."},
        {"name": "Concurrency", "description": "Developing concurrent programs using Rust's memory safety and ownership model."},
        {"name": "WebAssembly", "description": "Writing efficient, fast code for the web using Rust and compiling to WebAssembly."},
        {"name": "Embedded Systems", "description": "Developing software for low-level systems such as microcontrollers."}
    ],
    "PHP": [
        {"name": "Web Development", "description": "Building dynamic websites and web applications with PHP and databases."},
        {"name": "WordPress", "description": "Developing plugins, themes, and custom applications on the WordPress platform."},
        {"name": "Backend Development", "description": "Creating server-side logic and interacting with databases using PHP and frameworks like Laravel."}
    ],
    "C#": [
        {"name": "Web Development", "description": "Building web applications with C# and the ASP.NET framework."},
        {"name": "Unity Game Development", "description": "Creating games for multiple platforms using Unity and C# scripting."},
        {"name": "Enterprise Applications", "description": "Developing large-scale enterprise applications with C# and the .NET ecosystem."},
        {"name": ".NET Framework", "description": "Building applications with the .NET framework using C# for cross-platform development."}
    ]
}

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_roles()
        print("Sucessfully created roles")
        self.create_users()
        self.create_programming_languages()
        self.create_subjects()
        self.create_default_lessons()
        self.assign_tutor_expertise() 
        self.create_tutor_availability() 
        self.users = User.objects.all()
        self.create_lessons()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def create_roles(self):
        """MUST BE CALLED FIRST ELSE USER DEFINITION BREAKS!!!"""
        for role in [UserRoles.STUDENT, UserRoles.TUTOR, UserRoles.ADMIN]:
            Role.objects.get_or_create(name=role)

    def generate_user_fixtures(self):
        for data in FIXED_USER_FIXTURES:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        roles = choices(
            [UserRoles.STUDENT, UserRoles.TUTOR, UserRoles.ADMIN],
            weights=[0.8, 0.15, 0.05],
            k=1
        )
        
        self.try_create_user({
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'roles': roles
        })
       
    def try_create_user(self, data):
        print(data)
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Failed to create {data.get('username')} {e}")

    def create_user(self, data: dict):
        """Create random user, assigning roles etc."""
        roles = data.get('roles', [UserRoles.STUDENT])

        role_objects = []
        
        for role_name in roles:
            try:
                role_obj = Role.objects.get(name=role_name)
                role_objects.append(role_obj)
            except ObjectDoesNotExist:
                raise ValueError(f"Role '{role_name}' does not exist in the database.")
        print(role_objects)
        # Create the user and assign roles
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_staff=data.get('is_staff', False),
            is_superuser=data.get('is_superuser', False)
        )
    
    def create_programming_languages(self):
        """Populate programming language table."""
        for lang in programming_languages:
            if not ProgrammingLanguage.objects.filter(name=lang).exists():
                ProgrammingLanguage.objects.create(name=lang)

    def create_subjects(self):
        """Create subjects for each programming language."""
        for language, subjects in programming_topics.items():
            language_instance = ProgrammingLanguage.objects.get(name=language)
            for subject in subjects:
                Subject.objects.get_or_create(
                    name=subject['name'],
                    language=language_instance,
                    defaults={'description': subject["description"]}
                )
    
    def create_default_lessons(self):
        """Create default lessons between Jane Doe (tutor) and Charlie (student)."""
        try:
            jane = User.objects.get(username='@janedoe')
            charlie = User.objects.get(username='@charlie')
            
            for lesson_data in DEFAULT_LESSONS:
                language = ProgrammingLanguage.objects.get(name=lesson_data['language'])
                subject = Subject.objects.get(name=lesson_data['subject_name'], language=language)
                
                lesson_date = timezone.now() + timedelta(days=lesson_data['days_from_now'])
                
                Lesson.objects.get_or_create(
                    student=charlie,
                    tutor=jane,
                    language=language,
                    subject=subject,
                    lesson_datetime=lesson_date
                )
        except Exception as e:
            print(f"Error creating default lessons: {e}")
                
    def create_lessons(self):
        """Create random lessons."""
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2025, 12, 31)
        lesson_cost = 10
        for i in range(500):
            tutor = choice(User.objects.filter(role="tutor"))
            student = choice(User.objects.filter(role="student"))
            language = choice(ProgrammingLanguage.objects.all())
            subject = choice(Subject.objects.filter(language=language))
            random_date = random_datetime(start_time, end_time)
            lesson_datetime = timezone.make_aware(random_date)
            
            if subject.exists():
                subject = choice(subject)
                random_date = random_datetime(start_time, end_time)
                lesson_datetime = timezone.make_aware(random_date)


            lesson = Lesson.objects.create(
                student=student, 
                tutor=tutor, 
                language=language, 
                subject=subject, 
                lesson_datetime=lesson_datetime
            )
            invoice =Invoice.objects.create(
                student=student,
                amount=lesson_cost,
                status=choice(['paid', 'unpaid']) )
            lesson.invoice= invoice
            lesson.save()
            
    def create_tutor_availability(self):
        """Generate random availability slots for tutors across a 24-hour range."""
        tutors = User.objects.filter(role='tutor')  
        for tutor in tutors:
            num_slots = randint(3, 10)  
            for _ in range(num_slots):
                date = self.faker.date_between(start_date='-30d', end_date='+30d') 
                start_hour = randint(0, 23)  
                start_minute = choice([0, 15, 30, 45])  
                start_time = time(start_hour, start_minute)

                max_end_hour = min(23, start_hour + randint(1, 3))  
                end_minute = start_minute if max_end_hour > start_hour else 59
                end_time = time(max_end_hour, end_minute)

                TutorAvailability.objects.get_or_create(
                    tutor=tutor,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    recurrence='none'  
                )
        print("Tutor availability slots seeded.")                    

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def random_datetime(start_time, end_time):
    """Create random times within the given window."""
    delta = end_time - start_time
    random_seconds = randint(0, int(delta.total_seconds()))
    return start_time + timedelta(seconds=random_seconds)

def create_invoices(self):
    """Generate invoices for students."""
    student_role = Role.objects.get(name=UserRoles.STUDENT)
    students = User.objects.filter(roles=student_role)
    lessons = Lesson.objects.filter(invoice__isnull=True)
    lesson_cost=10

    for lesson in lessons:
        
        invoice = Invoice.objects.create(
            student=lesson.student,
            amount=lesson_cost,
            status=choice(['paid', 'unpaid'])
        )
        lesson.invoice = invoice
        lesson.save() 