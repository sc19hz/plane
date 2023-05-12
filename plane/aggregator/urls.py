from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.index, name='index'),
    path('find_flight/', views.find_flight, name='find_flight'),
    path('flight_detail/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('order/', views.order, name='order'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('book_flight/', views.book_flight, name='book_flight'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('payment/<int:order_id>/login_payment/', views.login_payment, name='login_payment'),
    path('payment/<int:order_id>/requestkey/', views.request_key, name='request_key'),
    path('payment/<int:order_id>/pay/', views.pay, name='pay'),
]
