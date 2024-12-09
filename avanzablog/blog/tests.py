from django.test import TestCase
from django.contrib.auth.models import User
from blog.models import BlogPost
from rest_framework.test import APIClient
from django.urls import reverse

class BlogPostListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()  # Crear cliente de prueba
        self.user = User.objects.create_user(username='authenticated_user', password='test123')

        BlogPost.objects.create(author=self.user, title="Post público", content="Visible para todos", post_permissions='public')
        BlogPost.objects.create(author=self.user, title="Post autenticado", content="Visible solo para autenticados", post_permissions='authenticated')
        BlogPost.objects.create(author=self.user, title="Post del autor", content="Visible solo para el autor", post_permissions='author')
        BlogPost.objects.create(author=self.user, title="Post de equipo", content="Visible para el equipo", post_permissions='team')

    def test_get_public_posts(self):
        """Usuarios no autenticados deben ver solo posts públicos."""
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Post público")
