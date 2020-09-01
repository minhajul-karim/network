from django.test import TestCase
from django.db import IntegrityError

from . models import User, Follower

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

    def test_duplicate_follower_error(self):
        """Test error raise when trying to insert duplicate followers."""
        user1 = User.objects.get(username="xyz")
        user2 = User.objects.get(username="mkr")
        with self.assertRaises(IntegrityError):
            Follower.objects.create(user=user1, followed=user2)
