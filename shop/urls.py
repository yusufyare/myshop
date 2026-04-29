from django.urls import path
from . import views

app_name = 'shop' # Fixed: must be app_name

urlpatterns = [
    path('', views.product_list, name='product_list'),
    
    path('<slug:category_slug>/', 
         views.product_list, 
         name='product_list_by_category'), # Fixed: gave it a unique name
         
    path('<int:id>/<slug:slug>/', 
         views.product_detail, 
         name='product_detail'), # Fixed: removed the extra space
]