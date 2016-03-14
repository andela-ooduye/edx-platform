"""
Tests for Blocks Views
"""

import json

import ddt
from django.test import TestCase, RequestFactory
from unittest import skip

from student.tests.factories import UserFactory

from .. import adapters
from .. import views


@ddt.ddt
class TestAccessTokenView(TestCase):
    """
    Test class for AccessTokenView
    """

    dop_adapter = adapters.DOPAdapter()
    dot_adapter = adapters.DOTAdapter()

    def setUp(self):
        super(TestAccessTokenView, self).setUp()
        self.user = UserFactory()
        self.dot_app = self.dot_adapter.create_public_client(
            name='test dot application',
            user=self.user,
            redirect_uri='https://example.edx/redirect',
            client_id='dot-app-client-id',
        )
        self.dop_client = self.dop_adapter.create_public_client(
            name='test dop client',
            user=self.user,
            redirect_uri='https://example.edx/redirect',
            client_id='dop-app-client-id',
        )

    def _post_access_token_request(self, user, client):
        """
        Make an HTTP POST request a token for the given user and client.

        Returns an HTTP Response.
        """
        token_view = views.AccessTokenView.as_view()
        request = RequestFactory().post('/', {
            'client_id': client.client_id,
            'grant_type': 'password',
            'username': user.username,
            'password': 'test',
        })
        return token_view(request)

    @ddt.data('dop_client', 'dot_app')
    def test_access_token_fields(self, client_attr):
        client = getattr(self, client_attr)
        response = self._post_access_token_request(self.user, client)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('access_token', data)
        self.assertIn('expires_in', data)
        self.assertIn('scope', data)
        self.assertIn('token_type', data)

    def test_dot_access_token_provides_refresh_token(self):
        response = self._post_access_token_request(self.user, self.dot_app)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('refresh_token', data)

    def test_dop_access_token(self):
        response = self._post_access_token_request(self.user, self.dop_client)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('refresh_token', data)


@ddt.ddt
class TestAuthorizationView(TestCase):
    """
    Test class for AccessTokenView
    """

    dop_adapter = adapters.DOPAdapter()

    def setUp(self):
        super(TestAuthorizationView, self).setUp()
        self.user = UserFactory()
        self.dop_client = self.dop_adapter.create_confidential_client(user=self.user, client_id='dop-app-client-id')

    def test_authorization_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.post('/oauth2/authorize/', {
            'client_id': self.dop_client.client_id,  # DOT is not yet supported (MA-2124)
            'response_type': 'code',
            'state': 'random_state_string',
            'redirect_uri': 'http://example.edx/redirect',
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        # check form is in context and form params are valid
        context = response.context  # pylint: disable=no-member
        self.assertIn('form', context)
        self.assertIsNone(context['form']['authorize'].value())

        self.assertIn('oauth_data', context)
        oauth_data = context['oauth_data']
        self.assertEqual(oauth_data['redirect_uri'], 'http://example.edx/redirect')
        self.assertEqual(oauth_data['state'], 'random_state_string')
