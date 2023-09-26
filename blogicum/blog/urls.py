from blog import views
from django.urls import path

app_name = 'blog'

urlpatterns = [
    path('',
         views.IndexListView.as_view(),
         name='index'),
    path('posts/create/', views.PostsCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post_id>/edit/',
         views.PostsUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentEditView.as_view(),
         name='edit_comment'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<username>/',
         views.ProfileListView.as_view(),
         name='profile'),
    path('profile/edit',
         views.ProfileEditView.as_view(),
         name='edit_profile'),
]
