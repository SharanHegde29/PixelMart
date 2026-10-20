from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/signup/', views.signup, name='signup'),
    
    path('product/add/', views.add_product, name='add_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('product/update/<int:pk>/', views.update_product, name='update_product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    path('product/<int:pk>/buy/', views.buy_product, name='buy_product'),
    
    path('my-orders/', views.my_orders, name='my_orders'),
    
    path('order/confirm/<int:pk>/', views.confirm_order, name='confirm_order'),

    path('', views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)