from django.core.management.base import BaseCommand, CommandError

from tutorials.models import User, ProgrammingLanguage, Subject, Lesson

import pytz
from faker import Faker
from random import randint, choices

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
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
        self.create_users()
        self.create_programming_languages()
        self.create_subjects()
        self.users = User.objects.all()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        # Randomly assign roles, with more students than tutors and few admins
        role = choices(
            [User.STUDENT, User.TUTOR, User.ADMIN],
            weights=[0.8, 0.15, 0.05],
            k=1
        )[0]
        
        self.try_create_user({
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role
        })
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', User.STUDENT),  # Default to student if not specified
        )
    
    def create_programming_languages(self):
        """Populate programming language table."""
        for lang in programming_languages:
            ProgrammingLanguage.objects.create(name=lang)

    def create_subjects(self):
        """Create subtjects for each programming language."""
        for language, subjects in programming_topics.items():

            language_instance = ProgrammingLanguage.objects.get(name=language)

            for subject in subjects:
                Subject.objects.create(name=subject['name'],
                                       language=language_instance,
                                       description=subject["description"])
                
    def create_lessons():
        """TO IMPLEMENT ONCE BERNARDO HAS SORTED OUT ROLES"""
        pass

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'