from django.urls import path
from . import views

urlpatterns = [
    path("reporter/", views.ReporterView.as_view()),
    path("issues/", views.IssueView.as_view())
]