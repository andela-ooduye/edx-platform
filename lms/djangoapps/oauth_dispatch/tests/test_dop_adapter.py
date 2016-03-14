"""
Tests for Blocks Views
"""

from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from provider.oauth2 import models
from provider import constants

from student.tests.factories import UserFactory

from ..adapters import  DOPAdapter


class DOPAdapterTestCase(TestCase):
    """
    Test class for DOTAdapter.
    """

    adapter = DOPAdapter()

    def setUp(self):
        super(DOPAdapterTestCase, self).setUp()
        self.user = UserFactory()
        self.public_client = self.adapter.create_public_client(
            name='app',
            user=self.user,
            redirect_uri='https://example.edx/redirect',
            client_id='public-client-id')
        self.confidential_client = self.adapter.create_confidential_client(
            user=self.user,
            client_id='confidential-client-id'
        )

    def test_create_confidential_client(self):
        self.assertIsInstance(self.confidential_client, models.Client)
        self.assertEqual(self.confidential_client.client_id, 'confidential-client-id')
        self.assertEqual(self.confidential_client.client_type, constants.CONFIDENTIAL)

    def test_create_public_client(self):
        self.assertIsInstance(self.public_client, models.Client)
        self.assertEqual(self.public_client.client_id, 'public-client-id')
        self.assertEqual(self.public_client.client_type, constants.PUBLIC)

    def test_get_client(self):
        client = self.adapter.get_client(client_type=constants.CONFIDENTIAL)
        self.assertIsInstance(client, models.Client)
        self.assertEqual(client.client_type, constants.CONFIDENTIAL)

    def test_get_client_not_found(self):
        with self.assertRaises(models.Client.DoesNotExist):
            self.adapter.get_client(client_id='not-found')

    def test_get_client_for_token(self):
        token = models.AccessToken(
            user=self.user,
            client=self.public_client,
        )
        self.assertEqual(self.adapter.get_client_for_token(token), self.public_client)

    def test_get_access_token(self):
        token = models.AccessToken.objects.create(
            token='token-id',
            client=self.public_client,
            user=self.user,
            expires=now() + timedelta(days=30),
        )
        self.assertEqual(
            self.adapter.get_access_token(token_string='token-id'),
            token
        )
