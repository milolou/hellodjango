from django.contrib import admin
from django.urls import path

from vote import views

urlpatterns = [
    path('subjects/', views.show_subjects),
    path('subjects/teachers/', views.show_teachers),
    path('admin/', admin.site.urls),
    path('subjects/teachers/praise/',views.praise_or_criticize),
    path('subjects/teachers/criticize/',views.praise_or_criticize),
    path('register/',views.register,name='register'),
    path('login/',views.login),
    path('captcha/',views.get_captcha),
    path('logout/',views.logout),
    path('excel/',views.export_teachers_excel),
    path('teachers_data/',views.get_teachers_data),
    path('echart/',views.get_echart),
    path('jssubjects/',views.subjects_json),
    path('jsubjects/',views.jsubjects),
]
