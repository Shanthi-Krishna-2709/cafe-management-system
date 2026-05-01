from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('cart/', views.cart, name='cart'),
    path('add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('pdf/', views.pdf, name='pdf'),
    path('payment/', views.payment, name='payment'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('qr/', views.qr, name='qr'),
    path('about/', views.about, name='about'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('sales-report/', views.sales_report, name='sales_report'),
]
