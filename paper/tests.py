from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Library, Paper
from user.models import Account
from author.models import Author

class LibraryViewSetTestCase(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(authorId='author1', name='Author 1', paperCount=0, citationCount=0, hIndex=0)
        self.user = User.objects.create_user(username='jonathan', password='123')
        self.account = Account.objects.create(user=self.user)
        self.library = Library.objects.create(name='Library 1', owner=self.account)
        self.paper = Paper.objects.create(paperId='paper1', title='Paper 1', referenceCount=0, citationCount=0, publicationDate='2023-06-01')
        self.paper.authors.add(self.author)
    
    def test_create_library(self):
        url = reverse('paper:library-list')  # Use the name of the route as registered in your router
        data = {'name': 'Library 2', 'owner': self.account.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_library(self):
        url = reverse('paper:library-detail', kwargs={'pk': self.library.id})  # Use the name of the route as registered in your router
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_paper_to_library(self):
        url = reverse('paper:library-paper-add', kwargs={'library_pk': self.library.id})
        data = {'paperId': self.paper.paperId}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_remove_paper_from_library(self):
        self.library.papers.add(self.paper)
        url = reverse('paper:library-paper-remove', kwargs={'library_pk': self.library.id, 'pk': self.paper.paperId})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_move_paper_between_libraries(self):
        library2 = Library.objects.create(name='Library 2', owner=self.account)
        self.library.papers.add(self.paper)
        url = reverse('paper:library-paper-move', kwargs={'library_pk': self.library.id, 'pk': self.paper.paperId})
        data = {'targetLibraryId': library2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
