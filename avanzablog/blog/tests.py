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
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer

class BlogPostListViewTest(TestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()

        # Create users
        self.author = User.objects.create_user(username='author', password='password')
        self.team_member = User.objects.create_user(username='team_member', password='password')
        self.authenticated_user = User.objects.create_user(username='authenticated_user', password='password')

        # Create a group and assign it to users
        self.group = Group.objects.create(name="test-group")
        self.team_member.groups.add(self.group)
        self.author.groups.add(self.group)

        # Create posts with all four permission fields properly set
        self.public_post = BlogPost.objects.create(
            title="Public Post", content="Content", author=self.author, 
            is_public="read only", authenticated="none", team="none", owner="read and edit"
        )
        self.authenticated_post = BlogPost.objects.create(
            title="Authenticated Post", content="Content", author=self.author, 
            is_public="none", authenticated="read only", team="none", owner="read and edit"
        )
        self.team_post = BlogPost.objects.create(
            title="Team Post", content="Content", author=self.author, 
            is_public="none", authenticated="none", team="read and edit", owner="read and edit"
        )
        self.author_post = BlogPost.objects.create(
            title="Author Post", content="Content", author=self.author, 
            is_public="none", authenticated="none", team="none", owner="read and edit"
        )


    def test_anonymous_user_access(self):
        url = reverse('post-list')
        request = self.factory.get(url)
        response = BlogPostListView.as_view()(request)
        print("Anonymous user can see:", [post['title'] for post in response.data['results']])

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
        self.client = APIClient()
        
        # Crear usuarios
        self.user_1 = User.objects.create_user(username='user_1', password='testpass')
        self.user_2 = User.objects.create_user(username='user_2', password='testpass')
        
        # Crear grupos y asignar usuarios
        self.group1 = Group.objects.create(name='group1')
        self.group2 = Group.objects.create(name='group2')

        self.user_1.groups.add(self.group1)
        self.user_2.groups.add(self.group2)
        
        # Crear posts con permisos específicos
        self.post_1 = BlogPost.objects.create(
            author=self.user_1, 
            title="Post numero 1",
            content="contenido Post numero 1",
            is_public='read only',  # Cualquier usuario puede verlo
            authenticated='read only', 
            team='read and edit', 
            owner='read and edit'
        )

        self.post_2 = BlogPost.objects.create(
            author=self.user_2, 
            title="Post numero 2",
            content="contenido Post numero 2",
            is_public='none',  # Usuarios no autenticados no pueden verlo
            authenticated='read only',  # Solo autenticados pueden verlo
            team='read and edit', 
            owner='read and edit'
        )

        # Crear likes para cada post
        self.like_post_1_1 = Like.objects.create(user=self.user_2, post=self.post_1)
        self.like_post_1_2 = Like.objects.create(user=self.user_1, post=self.post_1)

        self.like_post_2_1 = Like.objects.create(user=self.user_2, post=self.post_2)
        self.like_post_2_2 = Like.objects.create(user=self.user_1, post=self.post_2)

    # def test_unauthenticated_user_sees_only_post_1_with_two_likes(self):
    #     """Un usuario no autenticado solo debe ver el primer post y sus 2 likes."""
    #     response = self.client.get('api/likes/')
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Extraer IDs de posts visibles
    #     visible_post_ids = {like['post'] for like in response.data['results']}

    #     # Debe ver solo el post_1
    #     self.assertIn(self.post_1.id, visible_post_ids)
    #     self.assertNotIn(self.post_2.id, visible_post_ids)

    #     # Verificar los likes del post_1
    #     likes_post_1 = [like for like in response.data['results'] if like['post'] == self.post_1.id]
    #     self.assertEqual(len(likes_post_1), 2)

    # def test_authenticated_user_sees_both_posts_with_two_likes_each(self):
    #     """Un usuario autenticado debe ver ambos posts y cada uno con 2 likes."""
    #     self.client.login(username='user_1', password='testpass')
    #     response = self.client.get('api/likes/')
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Extraer IDs de posts visibles
    #     visible_post_ids = {like['post'] for like in response.data['results']}
        
    #     # Debe ver ambos posts
    #     self.assertIn(self.post_1.id, visible_post_ids)
    #     self.assertIn(self.post_2.id, visible_post_ids)

    #     # Verificar los likes de cada post
    #     likes_post_1 = [like for like in response.data['results'] if like['post'] == self.post_1.id]
    #     likes_post_2 = [like for like in response.data['results'] if like['post'] == self.post_2.id]

    #     self.assertEqual(len(likes_post_1), 2)
    #     self.assertEqual(len(likes_post_2), 2)



#     def test_authenticated_user_access(self):
#         response = self.perform_request(self.authenticated_user)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 2)  # Likes en publicaciones públicas y autenticadas
#         post_ids = [like['post'] for like in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)

#     def test_team_member_access(self):
#         response = self.perform_request(self.team_member)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 3)  # Likes en publicaciones públicas, autenticadas y de equipo
#         post_ids = [like['post'] for like in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)
#         self.assertIn(self.team_post.id, post_ids)

#     def test_author_access(self):
#         response = self.perform_request(self.author)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 4)  # Likes en todas las publicaciones
#         post_ids = [like['post'] for like in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)
#         self.assertIn(self.team_post.id, post_ids)
#         self.assertIn(self.author_post.id, post_ids)

# class CommentListViewTest(TestCase):
    
#     def setUp(self):
#         # Crear usuarios
#         self.author = User.objects.create_user(username='author', password='password')
#         self.team_member = User.objects.create_user(username='team_member', password='password')
#         self.authenticated_user = User.objects.create_user(username='authenticated_user', password='password')

#         # Crear grupo y asignar usuarios
#         self.group = Group.objects.create(name="test-group")
#         self.team_member.groups.add(self.group)
#         self.author.groups.add(self.group)

#         # Crear posts
#         self.public_post = BlogPost.objects.create(
#             title="Public Post", content="Content", post_permissions="public", author=self.author
#         )
#         self.authenticated_post = BlogPost.objects.create(
#             title="Authenticated Post", content="Content", post_permissions="authenticated", author=self.author
#         )
#         self.team_post = BlogPost.objects.create(
#             title="Team Post", content="Content", post_permissions="team", author=self.author
#         )
#         self.author_post = BlogPost.objects.create(
#             title="Author Post", content="Content", post_permissions="author", author=self.author
#         )

#         # Crear comentarios
#         Comment.objects.create(post=self.public_post, user=self.author, content="Comment on public post")
#         Comment.objects.create(post=self.authenticated_post, user=self.author, content="Comment on authenticated post")
#         Comment.objects.create(post=self.team_post, user=self.author, content="Comment on team post")
#         Comment.objects.create(post=self.author_post, user=self.author, content="Comment on author post")

#         # Inicializar el request factory
#         self.factory = APIRequestFactory()

#     def test_anonymous_user_access(self):
#         url = reverse('comment-list')
#         request = self.factory.get(url)
#         view = CommentListView.as_view()
#         response = view(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)  # Solo comentarios en publicaciones públicas
#         comment_data = response.data['results'][0]
#         self.assertEqual(comment_data['post'], self.public_post.id)  # Validar ID del post
#         self.assertEqual(comment_data['username'], "author")  # Validar autor del comentario
#         self.assertEqual(comment_data['content'], "Comment on public post")  # Validar contenido del comentario

#     def test_authenticated_user_access(self):
#         url = reverse('comment-list')
#         request = self.factory.get(url)
#         request.user = self.authenticated_user  # Simular un usuario autenticado
#         view = CommentListView.as_view()
#         response = view(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 2)  # Comentarios en publicaciones públicas y autenticadas
#         post_ids = [comment['post'] for comment in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)

#     def test_team_member_access(self):
#         url = reverse('comment-list')
#         request = self.factory.get(url)
#         request.user = self.team_member  # Simular un usuario miembro del equipo
#         view = CommentListView.as_view()
#         response = view(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 3)  # Comentarios en publicaciones públicas, autenticadas y de equipo
#         post_ids = [comment['post'] for comment in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)
#         self.assertIn(self.team_post.id, post_ids)

#     def test_author_access(self):
#         url = reverse('comment-list')
#         request = self.factory.get(url)
#         request.user = self.author  # Simular al autor como usuario autenticado
#         view = CommentListView.as_view()
#         response = view(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 4)  # Comentarios en todas las publicaciones
#         post_ids = [comment['post'] for comment in response.data['results']]
#         self.assertIn(self.public_post.id, post_ids)
#         self.assertIn(self.authenticated_post.id, post_ids)
#         self.assertIn(self.team_post.id, post_ids)
#         self.assertIn(self.author_post.id, post_ids)

# class BlogPostDetailViewTest(TestCase):

#     def setUp(self):
#         # Create users
#         self.author = User.objects.create_user(username="author", password="password")
#         self.other_user = User.objects.create_user(username="other_user", password="password")
#         self.superuser = User.objects.create_superuser(username="superuser", password="password")

#         # Create groups for team-based permissions
#         self.team_group = Group.objects.create(name="team_group")

#         # Assign the author to the group (for team-based permissions)
#         self.author.groups.add(self.team_group)

#         # Create posts with different permissions
#         self.post = BlogPost.objects.create(
#             title="Test Post",
#             content="Test Content",
#             post_permissions="team",  # Team permissions
#             author=self.author
#         )

#         self.post2 = BlogPost.objects.create(
#             title="Test Post 2",
#             content="Test Content 2",
#             post_permissions="public",  # Public permissions
#             author=self.author
#         )

#         self.post3 = BlogPost.objects.create(
#             title="Test Post 3",
#             content="Test Content 3",
#             post_permissions="author",  # Author permissions
#             author=self.author
#         )

#         self.post4 = BlogPost.objects.create(
#             title="Test Post 4",
#             content="Test Content 4",
#             post_permissions="authenticated",  # Authenticated permissions
#             author=self.author
#         )

#         # Initialize the APIRequestFactory
#         self.factory = APIRequestFactory()

#         # Create requests with different users
#         self.author_request = self.factory.get(f'/posts/{self.post.id}/')
#         self.author_request.user = self.author

#         self.other_user_request = self.factory.get(f'/posts/{self.post.id}/')
#         self.other_user_request.user = self.other_user

#         self.superuser_request = self.factory.get(f'/posts/{self.post.id}/')
#         self.superuser_request.user = self.superuser

#         # Same for POST, PATCH, DELETE requests
#         self.author_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
#         self.author_patch_request.user = self.author

#         self.other_user_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
#         self.other_user_patch_request.user = self.other_user

#         self.superuser_patch_request = self.factory.patch(f'/posts/{self.post.id}/', {'title': 'Updated Title'})
#         self.superuser_patch_request.user = self.superuser

#         self.author_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
#         self.author_delete_request.user = self.author

#         self.other_user_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
#         self.other_user_delete_request.user = self.other_user

#         self.superuser_delete_request = self.factory.delete(f'/posts/{self.post.id}/')
#         self.superuser_delete_request.user = self.superuser

# #############################GET#################################


#     def test_get_post_public(self):
#         # Test GET request for a public post (should be accessible by anyone)
#         view = BlogPostDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post2.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.post2.title)

#     def test_get_post_authenticated(self):
#         # Test GET request for an authenticated post (should be accessible by authenticated users)
#         view = BlogPostDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post4.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.post4.title)

#     def test_get_post_team(self):
#         # Test GET request for a team post (should be accessible by team members)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.post.title)

#     def test_get_post_author(self):
#         # Test GET request for an author post (should be accessible by the author)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_request, pk=self.post3.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.post3.title)

#     def test_get_post_unauthorized(self):
#         # Test GET request for unauthenticated user
#         view = BlogPostDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_get_post_superuser(self):
#         # Test GET request for a superuser (should have access to all posts)
#         view = BlogPostDetailView.as_view()
#         response = view(self.superuser_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.post.title)





# #################################patch#####################################

#     def test_patch_post_team(self):
#         # Test PATCH request for a team post (should be accessible by team members)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_patch_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], 'Updated Title')

#     def test_patch_post_author(self):
#         # Test PATCH request for an author post (should be accessible by the author)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_patch_request, pk=self.post3.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], 'Updated Title')

#     def test_patch_post_superuser(self):
#         # Test PATCH request for a superuser (should succeed for any post)
#         view = BlogPostDetailView.as_view()
#         response = view(self.superuser_patch_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], 'Updated Title')

#     #verificamos si un usuario no registrado puede editar un post
#     def test_patch_post_unauthorized(self):
#         #test for an unauthenticated user
#         view = BlogPostDetailView.as_view()
#         response = view(self.other_user_patch_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



# ##############################DELETE###########################

#     def test_delete_post_team(self):
#         # Test DELETE request for a team post (should be accessible by team members)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_delete_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         with self.assertRaises(BlogPost.DoesNotExist):
#             BlogPost.objects.get(id=self.post.id)
    
#     def test_delete_post_author(self):
#         # Test DELETE request for an author post (should be accessible by the author)
#         view = BlogPostDetailView.as_view()
#         response = view(self.author_delete_request, pk=self.post3.id)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         with self.assertRaises(BlogPost.DoesNotExist):
#             BlogPost.objects.get(id=self.post3.id)



#    # Verify that an unauthenticated user cannot delete a post
#     def test_delete_post_unauthorized(self):
#         # Test for an unauthenticated user
#         view = BlogPostDetailView.as_view()
#         response = view(self.other_user_delete_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#     def test_delete_post_superuser(self):
#         # Test DELETE request for a superuser (should succeed for any post)
#         view = BlogPostDetailView.as_view()
#         response = view(self.superuser_delete_request, pk=self.post.id)#verifica si un superusuario puede eliminar un post
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) #verifica si el post fue eliminado
#         with self.assertRaises(BlogPost.DoesNotExist): #verifica si el post fue eliminado
#             BlogPost.objects.get(id=self.post.id)



# from unittest import mock


# class CommentDetailViewTest(TestCase):
    
#     def setUp(self):
#         # Create users
#         self.author = User.objects.create_user(username="author", password="password")
#         self.other_user = User.objects.create_user(username="other_user", password="password")
#         self.superuser = User.objects.create_superuser(username="superuser", password="password")
        
#         # Create groups for team permissions
#         self.team_group = Group.objects.create(name="Team")  # Example for team permission group
#         self.author.groups.add(self.team_group)  # Assign author to the team group
#         self.other_user.groups.add(self.team_group)  # Assign other_user to the team group, if they should also have access

#         # Create a post, este post puede camboiar de permisos para probar los diferentes casos 
#         self.post = BlogPost.objects.create(
#             title="Test Post",
#             content="Test Content",
#             post_permissions="team",  # Team permissions
#             author=self.author
#         )

#         # Create a comment on the post (optional for initial setup)
#         self.comment = Comment.objects.create(
#             post=self.post,
#             user=self.author,
#             content="Test Comment"
#         )

#         # Initialize the APIRequestFactory
#         self.factory = APIRequestFactory()

#         # Create requests with different users
#         self.author_request = self.factory.get(f'/comments/') #obtenemos comentarios como autor
#         self.author_request.user = self.author  # Author is part of the team
        
#         self.other_user_request = self.factory.get(f'/comments/') #obtenemos comentarios como otro usuario
#         self.other_user_request.user = self.other_user  # Other user is also part of the team

#         self.superuser_request = self.factory.get(f'/comments/') #obtenemos comentarios como superusuario
#         self.superuser_request.user = self.superuser  # Superuser can always access

#         # Create comment request for POST (via CommentListView and assuming filtering in view)
#         self.comment_request = self.factory.post(
#             f'/comments/',  # The URL for comment creation
#             {'content': 'New comment from author', 'post': self.post.id},  # Pass post id in the data
#             format='json'
#         )
#         self.comment_request.user = self.author  # Comment request from author



#     def test_get_comments_public_post(self):
#         # Test GET request for a public post
#         view = CommentDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id) #verifica si un usuario no registrado puede ver los comentarios de un post
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_get_comments_authenticated_post(self):
#         #get a comment from a post with authenticated permissions
#         self.post.post_permissions = "authenticated"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
        

#     def test_get_comments_team_post(self):
#         #get a comment from a post with team permissions
#         self.post.post_permissions = "team"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_get_comments_author_post(self):
#         # Test GET request for an author post
#         self.post.post_permissions = "author"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)


#     def test_posts_comment_public_post(self):
#         #test in order to prove if whichever user can add a commet to a public post
#         self.post.post_permissions = "public"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_post_comment_authenticated_post(self):
#         #test in order  to prove if a authenticated user can add a comment to a post with authenticated permissions
#         self.post.post_permissions = "authenticated"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)


#     def test_post_comment_team_post(self):
#         #test in order to prove if a team member can add a comment to a post with team permissions
#         self.post.post_permissions = "team"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_post_comment_author_post(self):
#         #test in order to prove if the author can add a comment to a post with author permissions
#         self.post.post_permissions = "author"
#         self.post.save()
#         view = CommentDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_post_comment_superuser(self):
#         #test in order to prove if a superuser can add a comment to a post
#         view = CommentDetailView.as_view()
#         response = view(self.superuser_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_post_comment_without_content(self):
#         # Test POST request without content
#         request = self.factory.post(
#             f'/comments/{self.post.id}/',  # Correct URL path for posting a comment
#             {'content': ''},  # Sending an empty content
#             format='json'
#         )
#         request.user = self.author  # Simulate an authenticated user with proper permissions

#         # Mock permission checks to bypass them for this test
#         with mock.patch.object(CommentDetailView, 'check_object_permissions', return_value=None):
#             response = CommentDetailView.as_view()(request, pk=self.post.id)

#         # Assert that the response status code is 400 BAD REQUEST
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Assert that the response contains the expected error detail
#         self.assertEqual(
#             response.data['detail'], 
#             "El contenido del comentario es obligatorio."
#         )

#     def test_post_comment_for_unauthenticated_user(self):
#         # Test POST request to add a comment as an unauthenticated user
#         unauthenticated_request = self.factory.post(
#             f'/comments/{self.post.id}/',  # Updated to match your CommentDetailView URL
#             {'content': 'Unauthenticated user comment'}, 
#             format='json'
#         )
#         unauthenticated_request.user = AnonymousUser()  # Simulate an unauthenticated user

#         # Use CommentDetailView to handle the request
#         response = CommentDetailView.as_view()(unauthenticated_request, pk=self.post.id)

#         # Assert that the response status code is 403 FORBIDDEN
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             response.data.get('detail'), 
#             'Authentication credentials were not provided.'  # Optional: Verify the response message
#         )

#     def test_post_comment_for_non_existing_post(self):
#         # Test POST request for a non-existing post (should return 404)
#         view = CommentDetailView.as_view()
#         response = view(self.comment_request, pk=9999)  # Non-existent post
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_get_comments_for_post_with_no_comments(self):
#         # Test GET request for a post that has no comments
#         # Create a post with no comments
#         post_without_comments = BlogPost.objects.create(
#             title="Post Without Comments",
#             content="Test Content",
#             post_permissions="public",  # Public permissions
#             author=self.author
#         )
#         view = CommentDetailView.as_view()
#         response = view(self.other_user_request, pk=post_without_comments.id)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data['detail'], "No hay comentarios para este post.")

#     def test_get_comments_for_post_with_comments(self):
#         # Test GET request for a post that has comments
#         view = CommentDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)  # Only one comment exists
#         self.assertEqual(response.data[0]['content'], self.comment.content)


# class LikeDetailViewTest(TestCase):

#     def setUp(self):
#         # Create users
#         self.author = User.objects.create_user(username="author", password="password")
#         self.other_user = User.objects.create_user(username="other_user", password="password")
#         self.superuser = User.objects.create_superuser(username="superuser", password="password")
        
#         # Create groups for team permissions
#         self.team_group = Group.objects.create(name="Team")  # Example for team permission group
#         self.author.groups.add(self.team_group)  # Assign author to the team group
#         self.other_user.groups.add(self.team_group)  # Assign other_user to the team group, if they should also have access

#         # Create a post, this post can change permissions to test different cases 
#         self.post = BlogPost.objects.create(
#             title="Test Post",
#             content="Test Content",
#             post_permissions="team",  # Team permissions
#             author=self.author
#         )

#         # Initialize the APIRequestFactory
#         self.factory = APIRequestFactory()

#         # Create requests with different users
#         self.author_request = self.factory.get(f'/likes/{self.post.id}/')  # Author requests likes for this post
#         force_authenticate(self.author_request, user=self.author)  # Force authenticate the author
        
#         self.other_user_request = self.factory.get(f'/likes/{self.post.id}/')  # Other user requests likes for this post
#         force_authenticate(self.other_user_request, user=self.other_user)  # Force authenticate the other user
        
#         self.superuser_request = self.factory.get(f'/likes/{self.post.id}/')  # Superuser requests likes for this post
#         force_authenticate(self.superuser_request, user=self.superuser)  # Force authenticate the superuser

#         # Create like request for POST (via LikeDetailView and assuming filtering in view)
#         self.like_request = self.factory.post(
#             f'/likes/{self.post.id}/',  # The URL for liking a post (include post id)
#             {'post': self.post.id},  # Pass post id in the data
#             format='json'
#         )
#         force_authenticate(self.like_request, user=self.author)  # Like request from author

#     def test_get_likes_public_post(self):
#         # Test GET request for a public post
#         self.post.post_permissions = "public"
#         self.post.save()
#         view = LikeDetailView.as_view()
#         response = view(self.other_user_request, pk=self.post.id)  # Check if a non-registered user can see likes
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)  # No likes initially

#     def test_get_likes_authenticated_post(self):
#         # Get likes for a post with authenticated permissions
#         self.post.post_permissions = "authenticated"
#         self.post.save()
#         view = LikeDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)  # No likes yet

#     def test_get_likes_team_post(self):
#         # Get likes for a post with team permissions
#         self.post.post_permissions = "team"
#         self.post.save()
#         view = LikeDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)  # No likes initially

#     def test_get_likes_author_post(self):
#         # Test GET request for an author post
#         self.post.post_permissions = "author"
#         self.post.save()
#         view = LikeDetailView.as_view()
#         response = view(self.author_request, pk=self.post.id)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)  # No likes initially

# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth.models import User
# from blog.models import BlogPost

# class BlogPostCreateViewTest(APITestCase):

#     def setUp(self):
#         # Set up users
#         self.user1 = User.objects.create_user(username='testuser1', password='password')
#         self.user2 = User.objects.create_user(username='testuser2', password='password')

#         # Define the URL for creating a post
#         self.url = reverse('post-create')

#     def test_create_post_authenticated(self):
#         """Test if an authenticated user can create a post."""
#         self.client.login(username='testuser1', password='password')

#         data = {
#             'title': 'Test Post',
#             'content': 'This is a test content for a blog post',
#         }

#         response = self.client.post(self.url, data, format='json')

#         # Assert that the response status is HTTP 201 Created
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         # Check that the post is created and belongs to the correct user
#         post = BlogPost.objects.get(id=response.data['id'])
#         self.assertEqual(post.author.username, 'testuser1')
#         self.assertEqual(post.title, data['title'])

#     def test_create_post_unauthenticated(self):
#         """Test if an unauthenticated user cannot create a post."""
#         data = {
#             'title': 'Test Post',
#             'content': 'This is a test content for a blog post',
#         }

#         response = self.client.post(self.url, data, format='json')

#         # Assert that the response status is HTTP 401 Unauthorized
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#         # Assert that the error message matches the expected detail
#         self.assertEqual(response.data['detail'], 'Debes estar autenticado para crear un post.')

#     def test_create_post_invalid_data(self):
#         """Test if creating a post with invalid data returns a 400 error."""
#         self.client.login(username='testuser1', password='password')

#         # Missing content field
#         data = {
#             'title': 'Test Post',
#         }

#         response = self.client.post(self.url, data, format='json')

#         # Assert that the response status is HTTP 400 Bad Request
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Check that the error message includes a validation error for the missing content
#         self.assertIn('content', response.data)


# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth.models import User
# from blog.models import BlogPost, Comment

# class CommentDeleteViewTest(APITestCase):

#     def setUp(self):
#         # Set up users
#         self.user1 = User.objects.create_user(username='testuser1', password='password')
#         self.user2 = User.objects.create_user(username='testuser2', password='password')

#         # Set up a blog post
#         self.post = BlogPost.objects.create(
#             title='Test Post',
#             content='This is a test content for a blog post',
#             author=self.user1,
#             post_permissions='public'
#         )

#         # Set up comments for the post
#         self.comment1 = Comment.objects.create(post=self.post, user=self.user1, content="User 1's comment")
#         self.comment2 = Comment.objects.create(post=self.post, user=self.user2, content="User 2's comment")

#         # Define the URLs for the tests
#         self.url_comment1 = reverse('comment-delete', kwargs={'pk': self.comment1.pk})  # URL to delete comment1
#         self.url_comment2 = reverse('comment-delete', kwargs={'pk': self.comment2.pk})  # URL to delete comment2

#     def test_delete_comment_author(self):
#         """Test if the author can delete their own comment."""
#         self.client.login(username='testuser1', password='password')
#         response = self.client.delete(self.url_comment1)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_delete_comment_not_author(self):
#         """Test if a user who is not the author of the comment cannot delete it."""
#         self.client.login(username='testuser2', password='password')
#         response = self.client.delete(self.url_comment1)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_delete_comment_unauthenticated(self):
#         """Test if an unauthenticated user cannot delete a comment."""
#         response = self.client.delete(self.url_comment1)
#         self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)

#     def test_delete_comment_not_found(self):
#         """Test if trying to delete a non-existing comment returns a 404 error."""
#         self.client.login(username='testuser1', password='password')
#         response = self.client.delete(reverse('comment-delete', kwargs={'pk': 999}))  # Non-existing comment ID
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_delete_comment_team_member(self):
#         """Test if a team member can delete another user's comment when post permissions are set to 'team'."""
#         # Create a team and add the users to it
#         team = Group.objects.create(name='team')
#         self.user1.groups.add(team)
#         self.user2.groups.add(team)

#         # Change the post permissions to 'team'
#         self.post.post_permissions = 'team'
#         self.post.save()

#         # Log in as the team member
#         self.client.login(username='testuser2', password='password')

#         # Try to delete the other user's comment
#         response = self.client.delete(self.url_comment1)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User, Group
# from blog.models import BlogPost, Comment, Like

# class BlogPostSerializerTest(APITestCase):

#     def setUp(self):
#         # Create users
#         self.user1 = User.objects.create_user(username='testuser1', password='password')
#         self.user2 = User.objects.create_user(username='testuser2', password='password')

#         # Create a group
#         self.group = Group.objects.create(name='test_group')

#         # Assign user1 to the group
#         self.user1.groups.add(self.group)

#         # Create a blog post
#         self.post = BlogPost.objects.create(
#             title='Test Blog Post',
#             content='This is a test content for the blog post.',
#             author=self.user1,
#             post_permissions='public'
#         )

#         # Add likes and comments to the post
#         self.like = Like.objects.create(post=self.post, user=self.user1)
#         self.comment1 = Comment.objects.create(post=self.post, user=self.user1, content="First comment")
#         self.comment2 = Comment.objects.create(post=self.post, user=self.user2, content="Second comment")

#     def test_serializer_likes_count(self):
#         """Test if the 'likes_count' field returns the correct number of likes."""
#         serializer = BlogPostSerializer(self.post)
#         data = serializer.data
#         self.assertEqual(data['likes_count'], 1)  # One like for the post

#     def test_serializer_comments_count(self):
#         """Test if the 'comments_count' field returns the correct number of comments."""
#         serializer = BlogPostSerializer(self.post)
#         data = serializer.data
#         self.assertEqual(data['comments_count'], 2)  # Two comments on the post

#     def test_serializer_excerpt(self):
#         """Test if the 'excerpt' field returns the correct excerpt."""
#         serializer = BlogPostSerializer(self.post)
#         data = serializer.data
#         self.assertEqual(data['excerpt'], 'This is a test content for the blog post.')  # First 200 characters

#     def test_serializer_equipo(self):
#         """Test if the 'equipo' field returns the correct group name."""
#         serializer = BlogPostSerializer(self.post)
#         data = serializer.data
#         self.assertEqual(data['equipo'], 'test_group')  # User1 belongs to 'test_group'


#     def test_serializer_username_field(self):
#         """Test if the 'username' field correctly serializes the author's username."""
#         serializer = BlogPostSerializer(self.post)
#         data = serializer.data
#         self.assertEqual(data['username'], 'testuser1')  # The author's username should be 'testuser1'


# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User
# from blog.models import BlogPost, Comment

# class CommentSerializerTest(APITestCase):

#     def setUp(self):
#         # Create users
#         self.user1 = User.objects.create_user(username='testuser1', password='password')
#         self.user2 = User.objects.create_user(username='testuser2', password='password')

#         # Create a blog post
#         self.post = BlogPost.objects.create(
#             title='Test Blog Post',
#             content='This is a test content for the blog post.',
#             author=self.user1,
#             post_permissions='public'
#         )

#         # Create comments for the post
#         self.comment1 = Comment.objects.create(post=self.post, user=self.user1, content="First comment")
#         self.comment2 = Comment.objects.create(post=self.post, user=self.user2, content="Second comment")

#     def test_serializer_fields(self):
#         """Test if the fields are serialized correctly for a comment."""
#         serializer = CommentSerializer(self.comment1)
#         data = serializer.data
        
#         # Check that the fields are correct
#         self.assertEqual(data['id'], self.comment1.id)  # Check comment ID
#         self.assertEqual(data['post'], self.comment1.post.id)  # Check post ID (should serialize post ID)
#         self.assertEqual(data['username'], self.comment1.user.username)  # Check username
#         self.assertEqual(data['content'], self.comment1.content)  # Check content
#         self.assertEqual(data['created_at'], self.comment1.created_at.replace(tzinfo=None).isoformat() + 'Z')


#     def test_auto_assignment_of_user_and_post(self):
#         """Test that 'user' and 'post' fields are auto-assigned."""
#         comment_data = {
#             'content': 'This is a test comment.',
#             'created_at': '2024-12-13T15:29:39.436753Z',
#         }

#         # Create the serializer with the comment data
#         serializer = CommentSerializer(data=comment_data)

#         # Save the comment and check if 'user' and 'post' are auto-assigned
#         if serializer.is_valid():
#             comment = serializer.save(post=self.post, user=self.user1)  # Simulate the auto-assignment
#             self.assertEqual(comment.user, self.user1)  # Check if 'user' is correctly assigned
#             self.assertEqual(comment.post, self.post)  # Check if 'post' is correctly assigned



#     def test_serializer_empty_content(self):
#         """Test if the content field is serialized properly even if empty."""
#         # Create a comment with empty content
#         comment_empty_content = Comment.objects.create(post=self.post, user=self.user1, content="")
#         serializer = CommentSerializer(comment_empty_content)
#         data = serializer.data
        
#         # Check that content is an empty string
#         self.assertEqual(data['content'], "")

# from rest_framework.test import APITestCase
# from django.contrib.auth.models import User
# from blog.models import BlogPost, Like

# class LikeSerializerTest(APITestCase):

#     def setUp(self):
#         # Create users
#         self.user1 = User.objects.create_user(username='testuser1', password='password')
#         self.user2 = User.objects.create_user(username='testuser2', password='password')

#         # Create a blog post
#         self.post = BlogPost.objects.create(
#             title='Test Blog Post',
#             content='This is a test content for the blog post.',
#             author=self.user1,
#             post_permissions='public'
#         )

#         # Create likes for the post
#         self.like1 = Like.objects.create(post=self.post, user=self.user1)
#         self.like2 = Like.objects.create(post=self.post, user=self.user2)

#     def test_serializer_fields(self):
#         """Test if the fields are serialized correctly for a like."""
#         serializer = LikeSerializer(self.like1)
#         data = serializer.data
        
#         # Check that the fields are correct
#         self.assertEqual(data['id'], self.like1.id)  # Check like ID
#         self.assertEqual(data['post'], self.like1.post.id)  # Check post ID (should serialize post ID)
#         self.assertEqual(data['username'], self.like1.user.username)  # Check username
        
#         # Check created_at, adjusting the format to match the serialized format
#         self.assertEqual(data['created_at'], self.like1.created_at.replace(tzinfo=None).isoformat() + 'Z')



#     def test_auto_assignment_of_user_and_post(self):
#         """Test that 'user' and 'post' fields are auto-assigned when creating a like."""
        
#         # Create like data without 'user' and 'post'
#         like_data = {
#             'created_at': '2024-12-13T15:29:39.436753Z',
#         }
        
#         # Initialize the serializer without 'user' and 'post' (since they are read-only and should be auto-assigned)
#         serializer = LikeSerializer(data=like_data)

#         # Check if the serializer is valid
#         self.assertTrue(serializer.is_valid())  # It should be valid
        
#         # Save the like instance
#         like = serializer.save(post=self.post, user=self.user1)  # Simulate the auto-assignment

#         # Check if 'user' and 'post' are correctly assigned
#         self.assertEqual(like.user, self.user1)  # Check if 'user' is correctly assigned
#         self.assertEqual(like.post, self.post)  # Check if 'post' is correctly assigned

#     def test_serializer_multiple_likes(self):
#         """Test if the serializer correctly serializes multiple likes."""
#         likes = [self.like1, self.like2]
#         serializer = LikeSerializer(likes, many=True)
#         data = serializer.data
        
#         # Check that the serialized data contains the expected number of likes
#         self.assertEqual(len(data), 2)
        
#         # Check if each like is serialized correctly
#         self.assertEqual(data[0]['id'], self.like1.id)
#         self.assertEqual(data[1]['id'], self.like2.id)


# from rest_framework.test import APITestCase
# from rest_framework import status
# from blog.models import BlogPost
# from django.urls import reverse

# class BlogPostPaginationTest(APITestCase):
    
#     def setUp(self):
#         # Create multiple blog posts for pagination testing
#         self.user = User.objects.create_user(username='testuser', password='password')
#         for i in range(25):  # Create 25 posts for testing pagination
#             BlogPost.objects.create(
#                 title=f'Blog Post {i+1}',
#                 content=f'Content for blog post {i+1}',
#                 author=self.user,
#                 post_permissions='public'
#             )

#     def test_pagination(self):
#         url = reverse('post-list')  # Assuming you have a list view for blog posts
        
#         # Request the first page (default page_size=10)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check pagination fields
#         self.assertIn('current_page', response.data)
#         self.assertIn('total_pages', response.data)
#         self.assertIn('total_count', response.data)
#         self.assertIn('next_page_url', response.data)
#         self.assertIn('previous_page_url', response.data)
        
#         # Check that the number of results on the first page is 10
#         self.assertEqual(len(response.data['results']), 10)

#     def test_custom_page_size(self):
#         url = reverse('post-list')
        
#         # Request with custom page_size (5 per page)
#         response = self.client.get(url, {'page_size': 5})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check pagination fields
#         self.assertIn('current_page', response.data)
#         self.assertIn('total_pages', response.data)
#         self.assertIn('total_count', response.data)
#         self.assertIn('next_page_url', response.data)
#         self.assertIn('previous_page_url', response.data)
        
#         # Check that the number of results per page is 5
#         self.assertEqual(len(response.data['results']), 5)

#     def test_next_page(self):
#         url = reverse('post-list')
        
#         # Request the first page
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check for the next page URL
#         next_page_url = response.data['next_page_url']
#         self.assertIsNotNone(next_page_url)
        
#         # Request the next page
#         response = self.client.get(next_page_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_previous_page(self):
#         url = reverse('post-list')
        
#         # Request the second page with page_size=10 (to have at least 2 pages)
#         response = self.client.get(url, {'page': 2})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check for the previous page URL
#         previous_page_url = response.data['previous_page_url']
#         self.assertIsNotNone(previous_page_url)
        
#         # Request the previous page
#         response = self.client.get(previous_page_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_single_page(self):
#         url = reverse('post-list')
        
#         # Create only 5 blog posts, so only 1 page of results is needed
#         BlogPost.objects.all().delete()
#         for i in range(5):
#             BlogPost.objects.create(
#                 title=f'Blog Post {i+1}',
#                 content=f'Content for blog post {i+1}',
#                 author=self.user,
#                 post_permissions='public'
#             )
        
#         # Request the first page
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check that there is no next page URL
#         self.assertIsNone(response.data['next_page_url'])
#         self.assertIsNone(response.data['previous_page_url'])

# ### 2. Test LikePagination


# class LikePaginationTest(APITestCase):

#     def setUp(self):
#         # Create a user and a post to associate likes
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.post = BlogPost.objects.create(
#             title='Test Blog Post',
#             content='Content for blog post',
#             author=self.user,
#             post_permissions='public'
#         )
        
#         # Create multiple likes for the post
#         for i in range(40):  # Create 40 likes for testing pagination
#             Like.objects.create(post=self.post, user=self.user)

#     def test_pagination(self):
#         url = reverse('like-list')  # Assuming you have a list view for likes
        
#         # Request the first page (default page_size=20)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check pagination fields
#         self.assertIn('current_page', response.data)
#         self.assertIn('total_pages', response.data)
#         self.assertIn('total_count', response.data)
#         self.assertIn('next_page_url', response.data)
#         self.assertIn('previous_page_url', response.data)
        
#         # Check that the number of results on the first page is 20
#         self.assertEqual(len(response.data['results']), 20)

#     def test_custom_page_size(self):
#         url = reverse('like-list')
        
#         # Request with custom page_size (15 per page)
#         response = self.client.get(url, {'page_size': 15})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check pagination fields
#         self.assertIn('current_page', response.data)
#         self.assertIn('total_pages', response.data)
#         self.assertIn('total_count', response.data)
#         self.assertIn('next_page_url', response.data)
#         self.assertIn('previous_page_url', response.data)
        
#         # Check that the number of results per page is 15
#         self.assertEqual(len(response.data['results']), 15)

#     def test_next_page(self):
#         url = reverse('like-list')
        
#         # Request the first page
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check for the next page URL
#         next_page_url = response.data['next_page_url']
#         self.assertIsNotNone(next_page_url)
        
#         # Request the next page
#         response = self.client.get(next_page_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_previous_page(self):
#         url = reverse('like-list')
        
#         # Request the second page with page_size=20 (to have at least 2 pages)
#         response = self.client.get(url, {'page': 2})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check for the previous page URL
#         previous_page_url = response.data['previous_page_url']
#         self.assertIsNotNone(previous_page_url)
        
#         # Request the previous page
#         response = self.client.get(previous_page_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_single_page(self):
#         url = reverse('like-list')
        
#         # Create only 10 likes, so only 1 page of results is needed
#         Like.objects.all().delete()
#         for i in range(10):
#             Like.objects.create(post=self.post, user=self.user)
        
#         # Request the first page
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Check that there is no next page URL
#         self.assertIsNone(response.data['next_page_url'])
#         self.assertIsNone(response.data['previous_page_url'])
