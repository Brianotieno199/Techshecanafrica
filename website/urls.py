from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "blog/<slug:slug>/",
        views.blog_detail,
        name="blog_detail",
    ),

    path(
        "events/<int:event_id>/",
        views.event_detail,
        name="event_detail",
    ),

    path(
        "events/<int:event_id>/register/",
        views.event_register,
        name="event_register",
    ),

    path(
        "events/<int:event_id>/register/<str:link_id>/",
        views.event_register,
        name="event_register_category",
    ),

    path(
        "register/<str:link_id>/",
        views.event_register,
        name="event_register_by_link",
    ),

    path(
        "registration/<int:registration_id>/payment/",
        views.registration_payment,
        name="registration_payment",
    ),

    path(
        "registration/<int:registration_id>/success/",
        views.registration_success,
        name="registration_success",
    ),
]