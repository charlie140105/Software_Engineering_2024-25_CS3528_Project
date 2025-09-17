from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "homepage"

urlpatterns = [
                path('', views.home, name='home'),
                path('detail_page/<int:pk>/', views.detail_page, name='detail_page'),
                path('upload/', views.uploadImage, name='upload_item'),
                path('rti/<int:pk>/', views.rti_page, name='rti'),
                path('help_page/', views.help_page, name='help_page'),
                path('review-items/', views.review_items, name='review_items'),
                path('user_item/', views.user_item, name='user_item'),
                path('item/<int:pk>/edit/', views.item_edit, name='item_edit'),
                path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),
                path('register/', views.register, name='register'),
                path('login/', views.user_login, name='user_login'),
                path('logout/', views.user_logout, name='user_logout'),
                path('item/<int:item_id>/approve/', views.approve_item, name='approve_item'),
                path('item/<int:item_id>/reject/', views.reject_item, name='reject_item'),
                path('user_profile/', views.user_profile, name='user_profile'),
                path('user/<int:user_id>/approve/', views.approve_user, name='approve_user'),
                path('user/<int:user_id>/reject/', views.reject_user, name='reject_user'),
                path('return_item/<int:item_id>/', views.return_item, name='return_item'),
                path('update_permission/', views.update_user_permission, name='update_user_permission'),
                path('admin/item/<int:item_id>/delete/', views.admin_delete_item, name='admin_delete_item'),
              ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
