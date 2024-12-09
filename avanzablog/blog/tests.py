from django.test import TestCase
from django.contrib.auth.models import User, Group
from blog.models import BlogPost
from rest_framework.test import APIClient
from django.urls import reverse
class BlogPostListViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='authenticated_user', password='test123')
        self.client.login(username='authenticated_user', password='test123')

        BlogPost.objects.create(author=self.user, title="Post público", content="Visible para todos", post_permissions='public')
        BlogPost.objects.create(author=self.user, title="Post autenticado", content="Visible solo para autenticados", post_permissions='authenticated')
        BlogPost.objects.create(author=self.user, title="Post del autor", content="Visible solo para el autor", post_permissions='author')
        BlogPost.objects.create(author=self.user, title="Post de equipo", content="Visible para el equipo", post_permissions='team')
        # Crear cliente de prueba
        self.client = APIClient()

    def test_get_public_posts(self):
        """Usuarios no autenticados deben ver solo posts públicos."""
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Public Post")

    def test_get_authenticated_posts(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
        print(response.data)  # Depuración para ver los posts devueltos
        self.assertEqual(len(response.data), 3)  # Ajusta según el caso esperado


    def test_get_team_posts(self):
        """Usuarios en un grupo deben ver posts de tipo 'team'."""
        self.client.login(username='testuser', password='password')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)  # Public, Authenticated, Author, Team
        titles = [post['title'] for post in response.data]
        self.assertIn("Team Post", titles)

    def test_no_duplicate_posts(self):
        """No debe haber duplicados en la respuesta."""
        self.client.login(username='testuser', password='password')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(set([post['id'] for post in response.data])))

    def test_ordered_by_created_at(self):
        """Los posts deben estar ordenados por fecha de creación."""
        self.client.login(username='testuser', password='password')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        created_at_values = [post['created_at'] for post in response.data]
        self.assertEqual(created_at_values, sorted(created_at_values))
