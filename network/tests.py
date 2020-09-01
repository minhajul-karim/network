import datetime
from django.test import TestCase
from django.db import IntegrityError

from . models import User, Follower, Post, Like

# Create your tests here.


class NetworkTestCase(TestCase):

    def setUp(self):

        # Create users
        u1 = User.objects.create(
            username="xyz",
            email="something@someotherthing.com",
            password="abc123"
        )

        u2 = User.objects.create(
            username="mkr",
            email="something@someotherthingelse.com",
            password="1234567iok"
        )

        # Create followers
        Follower.objects.create(user=u1, followed=u1)
        Follower.objects.create(user=u1, followed=u2)
        Follower.objects.create(user=u2, followed=u1)

        # Create posts
        post1 = Post.objects.create(
            user=u1,
            time_posted=datetime.datetime.utcnow(),
            content="hello"
        )

        # Create likes
        Like.objects.create(user=u1, post=post1)
        Like.objects.create(user=u2, post=post1)

    def test_number_of_posts_of_user(self):
        """Test number of posts of a user."""
        user = User.objects.get(username="xyz")
        num_of_posts = Post.objects.filter(user=user).count()
        self.assertEqual(num_of_posts, 1)

    def test_number_of_likes(self):
        """Test number of likes for a post."""
        post = Post.objects.get(pk=1)
        self.assertEqual(post.likes.count(), 2)

    def test_duplicate_likes_exception(self):
        """Test exception for duplicate likes."""
        post = Post.objects.get(pk=1)
        user = User.objects.get(pk=1)
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=user, post=post)

    def test_number_of_followers(self):
        """Test number of followers of a user."""
        user = User.objects.get(username="xyz")
        self.assertEqual(user.followed_by.count(), 2)

    def test_valid_follower(self):
        """Tests valid followers."""
        user1 = User.objects.get(username="xyz")
        user2 = User.objects.get(username="mkr")
        follower = Follower.objects.get(user=user1, followed=user2)
        self.assertTrue(follower.is_valid_follower())

    def test_invalid_follower(self):
        """Test if a user can follow him/herself."""
        user = User.objects.get(username="xyz")
        follower = Follower.objects.get(user=user, followed=user)
        self.assertFalse(follower.is_valid_follower())

    def test_exception_for_duplicate_row_in_follower_table(self):
        """Test error raise when trying to insert duplicate followers."""
        user1 = User.objects.get(username="xyz")
        user2 = User.objects.get(username="mkr")
        with self.assertRaises(IntegrityError):
            Follower.objects.create(user=user1, followed=user2)

    def test_exception_for_user_who_does_not_follow_anyone(self):
        """Test exception for a user who does not follow anyone."""
        user = User.objects.create(
            username="mnop",
            email="qrst@uvw.xyz",
            password="1234567iok"
        )
        with self.assertRaises(Follower.DoesNotExist):
            Follower.objects.get(user=user)

    def test_exception_for_duplicate_username(self):
        """
        Test if proper exception is raised while creating a new user
        with existing username.
        """
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username="xyz",
                email="something@someotherthing.com",
                password="abc123"
            )
