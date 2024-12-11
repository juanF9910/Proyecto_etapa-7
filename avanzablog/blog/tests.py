from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import BlogPost, Like, Comment
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from .views import BlogPostListView,   BlogPostDetailView, LikeListView, CommentListView, BlogPostCreateView, CommentDeleteView, CommentDetailView, LikeDetailView
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from rest_framework.exceptions import PermissionDenied

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

class BlogPostDetailViewTest(TestCase):

    def setUp(self):
        # Create users
        self.author = User.objects.create_user(username="author", password="password")
        self.other_user = User.objects.create_user(username="other_user", password="password")
        self.superuser = User.objects.create_superuser(username="superuser", password="password")

        # Create groups for team-based permissions
        self.team_group = Group.objects.create(name="team_group")

        # Assign the author to the group (for team-based permissions)
        self.author.groups.add(self.team_group)

        # Create posts with different permissions
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="Test Content",
            post_permissions="team",  # Team permissions
            author=self.author
        )

        self.post2 = BlogPost.objects.create(
            title="Test Post 2",
            content="Test Content 2",
            post_permissions="public",  # Public permissions
            author=self.author
        )

        self.post3 = BlogPost.objects.create(
            title="Test Post 3",
            content="Test Content 3",
            post_permissions="author",  # Author permissions
            author=self.author
        )

        self.post4 = BlogPost.objects.create(
            title="Test Post 4",
            content="Test Content 4",
            post_permissions="authenticated",  # Authenticated permissions
            author=self.author
        )

        # Initialize the APIRequestFactory
        self.factory = APIRequestFactory()

        # Create requests with different users
        self.author_request = self.factory.get(f'/posts/{self.post.id}/')
        self.author_request.user = self.author

        self.other_user_request = self.factory.get(f'/posts/{self.post.id}/')
        self.other_user_request.user = self.other_user

        self.superuser_request = self.factory.get(f'/posts/{self.post.id}/')
        self.superuser_request.user = self.superuser

        # Same for POST, PATCH, DELETE requests
        self.author_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
        self.author_patch_request.user = self.author

        self.other_user_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
        self.other_user_patch_request.user = self.other_user

        self.superuser_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
        self.superuser_patch_request.user = self.superuser

        self.author_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
        self.author_delete_request.user = self.author

        self.other_user_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
        self.other_user_delete_request.user = self.other_user

        self.superuser_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
        self.superuser_delete_request.user = self.superuser

#############################GET#################################


    def test_get_post_public(self):
        # Test GET request for a public post (should be accessible by anyone)
        view = BlogPostDetailView.as_view()
        response = view(self.other_user_request, pk=self.post2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post2.title)

    def test_get_post_authenticated(self):
        # Test GET request for an authenticated post (should be accessible by authenticated users)
        view = BlogPostDetailView.as_view()
        response = view(self.other_user_request, pk=self.post4.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post4.title)

    def test_get_post_team(self):
        # Test GET request for a team post (should be accessible by team members)
        view = BlogPostDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)

    def test_get_post_author(self):
        # Test GET request for an author post (should be accessible by the author)
        view = BlogPostDetailView.as_view()
        response = view(self.author_request, pk=self.post3.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post3.title)

    def test_get_post_unauthorized(self):
        # Test GET request for unauthenticated user
        view = BlogPostDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_post_superuser(self):
        # Test GET request for a superuser (should have access to all posts)
        view = BlogPostDetailView.as_view()
        response = view(self.superuser_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)





#################################patch#####################################

    def test_patch_post_team(self):
        # Test PATCH request for a team post (should be accessible by team members)
        view = BlogPostDetailView.as_view()
        response = view(self.author_patch_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_patch_post_author(self):
        # Test PATCH request for an author post (should be accessible by the author)
        view = BlogPostDetailView.as_view()
        response = view(self.author_patch_request, pk=self.post3.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_patch_post_superuser(self):
        # Test PATCH request for a superuser (should succeed for any post)
        view = BlogPostDetailView.as_view()
        response = view(self.superuser_patch_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    #verificamos si un usuario no registrado puede editar un post
    def test_patch_post_unauthorized(self):
        #test for an unauthenticated user
        view = BlogPostDetailView.as_view()
        response = view(self.other_user_patch_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



##############################DELETE###########################

    def test_delete_post_team(self):
        # Test DELETE request for a team post (should be accessible by team members)
        view = BlogPostDetailView.as_view()
        response = view(self.author_delete_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(BlogPost.DoesNotExist):
            BlogPost.objects.get(id=self.post.id)
    
    def test_delete_post_author(self):
        # Test DELETE request for an author post (should be accessible by the author)
        view = BlogPostDetailView.as_view()
        response = view(self.author_delete_request, pk=self.post3.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(BlogPost.DoesNotExist):
            BlogPost.objects.get(id=self.post3.id)



   # Verify that an unauthenticated user cannot delete a post
    def test_delete_post_unauthorized(self):
        # Test for an unauthenticated user
        view = BlogPostDetailView.as_view()
        response = view(self.other_user_delete_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_delete_post_superuser(self):
        # Test DELETE request for a superuser (should succeed for any post)
        view = BlogPostDetailView.as_view()
        response = view(self.superuser_delete_request, pk=self.post.id)#verifica si un superusuario puede eliminar un post
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) #verifica si el post fue eliminado
        with self.assertRaises(BlogPost.DoesNotExist): #verifica si el post fue eliminado
            BlogPost.objects.get(id=self.post.id)



from unittest import mock


class CommentDetailViewTest(TestCase):
    
    def setUp(self):
        # Create users
        self.author = User.objects.create_user(username="author", password="password")
        self.other_user = User.objects.create_user(username="other_user", password="password")
        self.superuser = User.objects.create_superuser(username="superuser", password="password")
        
        # Create groups for team permissions
        self.team_group = Group.objects.create(name="Team")  # Example for team permission group
        self.author.groups.add(self.team_group)  # Assign author to the team group
        self.other_user.groups.add(self.team_group)  # Assign other_user to the team group, if they should also have access

        # Create a post, este post puede camboiar de permisos para probar los diferentes casos 
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="Test Content",
            post_permissions="team",  # Team permissions
            author=self.author
        )

        # Create a comment on the post (optional for initial setup)
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.author,
            content="Test Comment"
        )

        # Initialize the APIRequestFactory
        self.factory = APIRequestFactory()

        # Create requests with different users
        self.author_request = self.factory.get(f'/comments/') #obtenemos comentarios como autor
        self.author_request.user = self.author  # Author is part of the team
        
        self.other_user_request = self.factory.get(f'/comments/') #obtenemos comentarios como otro usuario
        self.other_user_request.user = self.other_user  # Other user is also part of the team

        self.superuser_request = self.factory.get(f'/comments/') #obtenemos comentarios como superusuario
        self.superuser_request.user = self.superuser  # Superuser can always access

        # Create comment request for POST (via CommentListView and assuming filtering in view)
        self.comment_request = self.factory.post(
            f'/comments/',  # The URL for comment creation
            {'content': 'New comment from author', 'post': self.post.id},  # Pass post id in the data
            format='json'
        )
        self.comment_request.user = self.author  # Comment request from author



    def test_get_comments_public_post(self):
        # Test GET request for a public post
        view = CommentDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id) #verifica si un usuario no registrado puede ver los comentarios de un post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_comments_authenticated_post(self):
        #get a comment from a post with authenticated permissions
        self.post.post_permissions = "authenticated"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        

    def test_get_comments_team_post(self):
        #get a comment from a post with team permissions
        self.post.post_permissions = "team"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_comments_author_post(self):
        # Test GET request for an author post
        self.post.post_permissions = "author"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_posts_comment_public_post(self):
        #test in order to prove if whichever user can add a commet to a public post
        self.post.post_permissions = "public"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_comment_authenticated_post(self):
        #test in order  to prove if a authenticated user can add a comment to a post with authenticated permissions
        self.post.post_permissions = "authenticated"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_post_comment_team_post(self):
        #test in order to prove if a team member can add a comment to a post with team permissions
        self.post.post_permissions = "team"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_comment_author_post(self):
        #test in order to prove if the author can add a comment to a post with author permissions
        self.post.post_permissions = "author"
        self.post.save()
        view = CommentDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_comment_superuser(self):
        #test in order to prove if a superuser can add a comment to a post
        view = CommentDetailView.as_view()
        response = view(self.superuser_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_comment_without_content(self):
        # Test POST request without content
        request = self.factory.post(
            f'/comments/{self.post.id}/',  # Correct URL path for posting a comment
            {'content': ''},  # Sending an empty content
            format='json'
        )
        request.user = self.author  # Simulate an authenticated user with proper permissions

        # Mock permission checks to bypass them for this test
        with mock.patch.object(CommentDetailView, 'check_object_permissions', return_value=None):
            response = CommentDetailView.as_view()(request, pk=self.post.id)

        # Assert that the response status code is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the response contains the expected error detail
        self.assertEqual(
            response.data['detail'], 
            "El contenido del comentario es obligatorio."
        )

    def test_post_comment_for_unauthenticated_user(self):
        # Test POST request to add a comment as an unauthenticated user
        unauthenticated_request = self.factory.post(
            f'/comments/{self.post.id}/',  # Updated to match your CommentDetailView URL
            {'content': 'Unauthenticated user comment'}, 
            format='json'
        )
        unauthenticated_request.user = AnonymousUser()  # Simulate an unauthenticated user

        # Use CommentDetailView to handle the request
        response = CommentDetailView.as_view()(unauthenticated_request, pk=self.post.id)

        # Assert that the response status code is 403 FORBIDDEN
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('detail'), 
            'Authentication credentials were not provided.'  # Optional: Verify the response message
        )

    def test_post_comment_for_non_existing_post(self):
        # Test POST request for a non-existing post (should return 404)
        view = CommentDetailView.as_view()
        response = view(self.comment_request, pk=9999)  # Non-existent post
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_for_post_with_no_comments(self):
        # Test GET request for a post that has no comments
        # Create a post with no comments
        post_without_comments = BlogPost.objects.create(
            title="Post Without Comments",
            content="Test Content",
            post_permissions="public",  # Public permissions
            author=self.author
        )
        view = CommentDetailView.as_view()
        response = view(self.other_user_request, pk=post_without_comments.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No hay comentarios para este post.")

    def test_get_comments_for_post_with_comments(self):
        # Test GET request for a post that has comments
        view = CommentDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one comment exists
        self.assertEqual(response.data[0]['content'], self.comment.content)


class LikeDetailViewTest(TestCase):
    
    def setUp(self):
        # Create users
        self.author = User.objects.create_user(username="author", password="password")
        self.other_user = User.objects.create_user(username="other_user", password="password")
        self.superuser = User.objects.create_superuser(username="superuser", password="password")
        
        # Create groups for team permissions
        self.team_group = Group.objects.create(name="Team")  # Example for team permission group
        self.author.groups.add(self.team_group)  # Assign author to the team group
        self.other_user.groups.add(self.team_group)  # Assign other_user to the team group, if they should also have access

        # Create a post, este post puede cambiar de permisos para probar los diferentes casos 
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="Test Content",
            post_permissions="team",  # Team permissions
            author=self.author
        )

        # Initialize the APIRequestFactory
        self.factory = APIRequestFactory()

        # Create requests with different users
        self.author_request = self.factory.get(f'/likes/')  # Author requests likes
        self.author_request.user = self.author  # Author is part of the team
        
        self.other_user_request = self.factory.get(f'/likes/')  # Other user requests likes
        self.other_user_request.user = self.other_user  # Other user is also part of the team

        self.superuser_request = self.factory.get(f'/likes/')  # Superuser requests likes
        self.superuser_request.user = self.superuser  # Superuser can always access

        # Create like request for POST (via LikeDetailView and assuming filtering in view)
        self.like_request = self.factory.post(
            f'/likes/',  # The URL for liking a post
            {'post': self.post.id},  # Pass post id in the data
            format='json'
        )
        self.like_request.user = self.author  # Like request from author

    def test_get_likes_public_post(self):
        # Test GET request for a public post
        self.post.post_permissions = "public"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)  # Check if a non-registered user can see likes
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No likes initially

    def test_get_likes_authenticated_post(self):
        # Get likes for a post with authenticated permissions
        self.post.post_permissions = "authenticated"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No likes yet

    def test_get_likes_team_post(self):
        # Get likes for a post with team permissions
        self.post.post_permissions = "team"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No likes initially

    def test_get_likes_author_post(self):
        # Test GET request for an author post
        self.post.post_permissions = "author"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No likes initially


    def test_post_like_authenticated_post(self):
        # Test if an authenticated user can like a post with authenticated permissions
        self.post.post_permissions = "authenticated"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)  # Authenticated user likes the post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)  # One like is added

        # Try liking the post again (should delete the existing like and return 200)
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Like eliminado.")  # Like removed

    def test_post_like_team_post(self):
        # Test if a team member can like a post with team permissions
        self.post.post_permissions = "team"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)  # Team member likes the post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)  # One like is added

    def test_post_like_public_post(self):
        # Test if any user can like a public post
        self.post.post_permissions = "public"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.other_user_request, pk=self.post.id)  # Any user likes the post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)  # One like is added


    def test_post_like_author_post(self):
        # Test if the author can like their own post
        self.post.post_permissions = "author"
        self.post.save()
        view = LikeDetailView.as_view()
        response = view(self.author_request, pk=self.post.id)  # Author likes their own post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)  # One like is added

    def test_post_like_superuser(self):
        # Test if a superuser can like a post
        view = LikeDetailView.as_view()
        response = view(self.superuser_request, pk=self.post.id)  # Superuser likes the post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)  # One like is added

    def test_post_like_without_permissions(self):
        # Test if a user without the right permissions can't like the post
        self.post.post_permissions = "authenticated"
        self.post.save()
        unauthenticated_request = self.factory.post(
            f'/likes/{self.post.id}/',
            {'post': self.post.id}, 
            format='json'
        )
        unauthenticated_request.user = AnonymousUser()
        
        response = LikeDetailView.as_view()(unauthenticated_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_like_existing_like(self):
        # Simulate the user liking a post and then removing the like
        self.post.post_permissions = "public"
        self.post.save()
        view = LikeDetailView.as_view()

        # First, like the post
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to like it again (should remove the existing like)
        response = view(self.author_request, pk=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Like eliminado.")  # Expect the detail message

