from django.contrib import admin
from tutorials.models import Role, User, ProgrammingLanguage, Subject, Lesson, LessonRequest, Invoice, TutorAvailability, CancellationRequest, ChangeRequest

#Registering models .
admin.site.register(Role)
admin.site.register(User)
admin.site.register(ProgrammingLanguage)
admin.site.register(Subject)
admin.site.register(Lesson)
admin.site.register(LessonRequest)
admin.site.register(TutorAvailability)
admin.site.register(ChangeRequest)
admin.site.register(CancellationRequest)
admin.site.register(Invoice)