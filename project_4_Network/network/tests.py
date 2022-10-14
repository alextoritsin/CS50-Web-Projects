from django.test import TestCase, Client
from django.db.models import Max
from .models import User, Post

# Create your tests here.

def create_user(name, email, pswrd):
    return User.objects.create(username=name, email=email, password=pswrd)

def create_posts(user_obj, num):
    for i in range(num):
        Post.objects.create(author=user_obj, content=f'Post#{i}')

class TestNetworkCase(TestCase):

    def setUp(self):
        user1 = create_user('user1', 'user1@mail.com', 'secret')
        user2 = create_user('user2', 'user2@mail.com', 'secret')


    def test_index_view_without_posts(self):
        c = Client()
        response = c.get('')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Posts Yet')


    def test_one_page(self):
        user = User.objects.get(username='user1')
        create_posts(user, 10)
        
        c = Client()
        response = c.get('')
        page_obj = response.context['page_obj']
        self.assertEqual(response.status_code, 200)
        self.assertFalse(page_obj.has_other_pages())


    def test_two_pages(self):
        user = User.objects.get(username='user1')
        create_posts(user, 11)
        
        c = Client()
        response = c.get('')
        page_obj = response.context['page_obj']
        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_obj.has_next())


    def test_max_users(self):

        c = Client()
        max_id = User.objects.all().aggregate(Max('id'))['id__max']
        response = c.get(f'/profile/{max_id + 1}')
        self.assertEqual(response.status_code, 404)


    def test_profile(self):
        user = User.objects.get(username='user1')
        create_posts(user, 5)

        c = Client()
        response = c.get(f'/profile/{user.id}')
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 5)
        self.assertContains(response, user.username)


    def test_following(self):
        user1 = User.objects.get(username='user1')
        user2 = User.objects.get(username='user2')
        user1.following.add(user2)
        user2.followers.add(user1)

        c = Client()
        resp_user1 = c.get(f"/profile/{user1.id}")
        self.assertContains(resp_user1, "1</b> Following")
        
        resp_user2 = c.get(f"/profile/{user2.id}")
        self.assertContains(resp_user2, "1</b> Followers")

    

