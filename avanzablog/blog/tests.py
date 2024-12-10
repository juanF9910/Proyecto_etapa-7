from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import BlogPost, Like, Comment
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from .views import BlogPostListView
from blog.views import LikeListView, CommentListView  # Importa la vista directamente si es necesario


class BlogPostListViewTest(TestCase):
    def setUp(self):
        # Create APIRequestFactory
        self.factory = APIRequestFactory()

        # Create users
        self.author = User.objects.create_user(username='author', password='password')
        self.team_member = User.objects.create_user(username='team_member', password='password')
        self.authenticated_user = User.objects.create_user(username='authenticated_user', password='password')

        # Create a group and assign it to users
        self.group = Group.objects.create(name="test-group")
        self.team_member.groups.add(self.group)
        self.author.groups.add(self.group)

        # Create posts
        self.public_post = BlogPost.objects.create(
            title="Public Post", content="Content", post_permissions="public", author=self.author
        )
        self.authenticated_post = BlogPost.objects.create(
            title="Authenticated Post", content="Content", post_permissions="authenticated", author=self.author
        )
        self.team_post = BlogPost.objects.create(
            title="Team Post", content="Content", post_permissions="team", author=self.author
        )
        self.author_post = BlogPost.objects.create(
            title="Author Post", content="Content", post_permissions="author", author=self.author
        )

    def test_anonymous_user_access(self):
        url = reverse('post-list')
        request = self.factory.get(url)
        response = BlogPostListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only public posts
        self.assertEqual(response.data['results'][0]['title'], "Public Post")

    def test_authenticated_user_access(self):
        url = reverse('post-list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.authenticated_user)
        response = BlogPostListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Public + Authenticated
        titles = [post['title'] for post in response.data['results']]
        self.assertIn("Public Post", titles)
        self.assertIn("Authenticated Post", titles)

    def test_team_member_access(self):
        url = reverse('post-list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.team_member)
        response = BlogPostListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Public, Authenticated, Team
        titles = [post['title'] for post in response.data['results']]
        self.assertIn("Public Post", titles)
        self.assertIn("Authenticated Post", titles)
        self.assertIn("Team Post", titles)

    def test_author_access(self):
        url = reverse('post-list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.author)
        response = BlogPostListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)  # All posts
        titles = [post['title'] for post in response.data['results']]
        self.assertIn("Public Post", titles)
        self.assertIn("Authenticated Post", titles)
        self.assertIn("Team Post", titles)
        self.assertIn("Author Post", titles)

class LikeListViewTest(TestCase):
    def setUp(self):
        # Crear usuarios
        self.author = User.objects.create_user(username='author', password='password')
        self.team_member = User.objects.create_user(username='team_member', password='password')
        self.authenticated_user = User.objects.create_user(username='authenticated_user', password='password')

        # Crear grupo y asignar usuarios
        self.group = Group.objects.create(name="test-group")
        self.team_member.groups.add(self.group)
        self.author.groups.add(self.group)

        # Crear posts
        self.public_post = BlogPost.objects.create(
            title="Public Post", content="Content", post_permissions="public", author=self.author
        )
        self.authenticated_post = BlogPost.objects.create(
            title="Authenticated Post", content="Content", post_permissions="authenticated", author=self.author
        )
        self.team_post = BlogPost.objects.create(
            title="Team Post", content="Content", post_permissions="team", author=self.author
        )
        self.author_post = BlogPost.objects.create(
            title="Author Post", content="Content", post_permissions="author", author=self.author
        )

        # Crear likes
        Like.objects.create(post=self.public_post, user=self.author)
        Like.objects.create(post=self.authenticated_post, user=self.author)
        Like.objects.create(post=self.team_post, user=self.author)
        Like.objects.create(post=self.author_post, user=self.author)

        # Inicializar el request factory
        self.factory = APIRequestFactory()

    def perform_request(self, user=None):
        """
        Helper function to perform requests with optional user authentication.
        """
        url = reverse('like-list')
        request = self.factory.get(url)
        if user:
            request.user = user
        view = LikeListView.as_view()
        return view(request)

    def test_anonymous_user_access(self):
        response = self.perform_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo likes en publicaciones públicas
        like_data = response.data['results'][0]
        self.assertEqual(like_data['post'], self.public_post.id)  # Validar ID del post
        self.assertEqual(like_data['username'], "author")  # Validar autor del like

    def test_authenticated_user_access(self):
        response = self.perform_request(self.authenticated_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Likes en publicaciones públicas y autenticadas
        post_ids = [like['post'] for like in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)

    def test_team_member_access(self):
        response = self.perform_request(self.team_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Likes en publicaciones públicas, autenticadas y de equipo
        post_ids = [like['post'] for like in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)
        self.assertIn(self.team_post.id, post_ids)

    def test_author_access(self):
        response = self.perform_request(self.author)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)  # Likes en todas las publicaciones
        post_ids = [like['post'] for like in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)
        self.assertIn(self.team_post.id, post_ids)
        self.assertIn(self.author_post.id, post_ids)

class CommentListViewTest(TestCase):
    
    def setUp(self):
        # Crear usuarios
        self.author = User.objects.create_user(username='author', password='password')
        self.team_member = User.objects.create_user(username='team_member', password='password')
        self.authenticated_user = User.objects.create_user(username='authenticated_user', password='password')

        # Crear grupo y asignar usuarios
        self.group = Group.objects.create(name="test-group")
        self.team_member.groups.add(self.group)
        self.author.groups.add(self.group)

        # Crear posts
        self.public_post = BlogPost.objects.create(
            title="Public Post", content="Content", post_permissions="public", author=self.author
        )
        self.authenticated_post = BlogPost.objects.create(
            title="Authenticated Post", content="Content", post_permissions="authenticated", author=self.author
        )
        self.team_post = BlogPost.objects.create(
            title="Team Post", content="Content", post_permissions="team", author=self.author
        )
        self.author_post = BlogPost.objects.create(
            title="Author Post", content="Content", post_permissions="author", author=self.author
        )

        # Crear comentarios
        Comment.objects.create(post=self.public_post, user=self.author, content="Comment on public post")
        Comment.objects.create(post=self.authenticated_post, user=self.author, content="Comment on authenticated post")
        Comment.objects.create(post=self.team_post, user=self.author, content="Comment on team post")
        Comment.objects.create(post=self.author_post, user=self.author, content="Comment on author post")

        # Inicializar el request factory
        self.factory = APIRequestFactory()

    def test_anonymous_user_access(self):
        url = reverse('comment-list')
        request = self.factory.get(url)
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo comentarios en publicaciones públicas
        comment_data = response.data['results'][0]
        self.assertEqual(comment_data['post'], self.public_post.id)  # Validar ID del post
        self.assertEqual(comment_data['username'], "author")  # Validar autor del comentario
        self.assertEqual(comment_data['content'], "Comment on public post")  # Validar contenido del comentario

    def test_authenticated_user_access(self):
        url = reverse('comment-list')
        request = self.factory.get(url)
        request.user = self.authenticated_user  # Simular un usuario autenticado
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Comentarios en publicaciones públicas y autenticadas
        post_ids = [comment['post'] for comment in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)

    def test_team_member_access(self):
        url = reverse('comment-list')
        request = self.factory.get(url)
        request.user = self.team_member  # Simular un usuario miembro del equipo
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Comentarios en publicaciones públicas, autenticadas y de equipo
        post_ids = [comment['post'] for comment in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)
        self.assertIn(self.team_post.id, post_ids)

    def test_author_access(self):
        url = reverse('comment-list')
        request = self.factory.get(url)
        request.user = self.author  # Simular al autor como usuario autenticado
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)  # Comentarios en todas las publicaciones
        post_ids = [comment['post'] for comment in response.data['results']]
        self.assertIn(self.public_post.id, post_ids)
        self.assertIn(self.authenticated_post.id, post_ids)
        self.assertIn(self.team_post.id, post_ids)
        self.assertIn(self.author_post.id, post_ids)
