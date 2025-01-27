from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentDetailView, CommentListCreateView, UserCommentsView, UserLikedPostsView, UserPostsView, PostLikeToggleView, CommentLikeToggleView

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('user/posts/', UserPostsView.as_view(), name='user-posts'),
    path('user/comments/', UserCommentsView.as_view(), name='user-comments'),
    path('user/liked-posts/', UserLikedPostsView.as_view(), name='user-liked-posts'),
    path('posts/<int:post_id>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('comments/<int:comment_id>/like/', CommentLikeToggleView.as_view(), name='comment-like-toggle'),
]
