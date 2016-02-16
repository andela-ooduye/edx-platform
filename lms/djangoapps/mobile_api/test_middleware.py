"""
tests for version based app upgrade middleware
"""
from datetime import datetime
import ddt
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from pytz import UTC
from mobile_api.middleware import AppVersionUpgrade
from mobile_api.models import AppVersionConfig


@ddt.ddt
class TestAppVersionUpgradeMiddleware(TestCase):
    """ Tests for version based app upgrade middleware """
    def setUp(self):
        super(TestAppVersionUpgradeMiddleware, self).setUp()
        self.middleware = AppVersionUpgrade()
        self.set_app_version_config()

    def set_app_version_config(self):
        """ creates configuration data for platform versions """
        AppVersionConfig(platform="ios", version="1.1.1", expire_at=None, enabled=True).save()
        AppVersionConfig(
            platform="ios",
            version="2.2.2",
            expire_at=datetime(2014, 01, 01, tzinfo=UTC),
            enabled=True
        ).save()
        AppVersionConfig(
            platform="ios",
            version="4.4.4",
            expire_at=datetime(9000, 01, 01, tzinfo=UTC),
            enabled=True
        ).save()
        AppVersionConfig(platform="ios", version="6.6.6", expire_at=None, enabled=True).save()

        AppVersionConfig(platform="android", version="1.1.1", expire_at=None, enabled=True).save()
        AppVersionConfig(
            platform="android",
            version="2.2.2",
            expire_at=datetime(2014, 01, 01, tzinfo=UTC),
            enabled=True
        ).save()
        AppVersionConfig(
            platform="android",
            version="4.4.4",
            expire_at=datetime(9000, 01, 01, tzinfo=UTC),
            enabled=True
        ).save()
        AppVersionConfig(platform="android", version="6.6.6", expire_at=None, enabled=True).save()

    @ddt.data(
        ("Mozilla/5.0 (Linux; Android 5.1; Nexus 5 Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
         "Version/4.0 Chrome/47.0.2526.100 Mobile Safari/537.36 edX/org.edx.mobile/2.0.0"),
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) "
         "Mobile/13C75 edX/org.edx.mobile/2.2.1"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 "
         "Safari/537.36"),
    )
    def test_non_mobile_app_requests(self, user_agent):
        fake_request = HttpRequest()
        fake_request.META['HTTP_USER_AGENT'] = user_agent
        self.assertIsNone(self.middleware.process_request(fake_request))
        fake_response = HttpResponse()
        response = self.middleware.process_response(fake_request, fake_response)
        self.assertEquals(200, response.status_code)
        with self.assertRaises(KeyError):
            response[AppVersionUpgrade.LATEST_VERSION_HEADER]
        with self.assertRaises(KeyError):
            response[AppVersionUpgrade.UPGRADE_DEADLINE_HEADER]

    @ddt.data(
        "edX/org.edx.mobile (6.6.6; OS Version 9.2 (Build 13C75))",
        "edX/org.edx.mobile (7.7.7; OS Version 9.2 (Build 13C75))",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/6.6.6",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/7.7.7",
    )
    def test_no_update(self, user_agent):
        fake_request = HttpRequest()
        fake_request.META['HTTP_USER_AGENT'] = user_agent
        self.assertIsNone(self.middleware.process_request(fake_request))
        fake_response = HttpResponse()
        response = self.middleware.process_response(fake_request, fake_response)
        self.assertEquals(200, response.status_code)
        with self.assertRaises(KeyError):
            response[AppVersionUpgrade.LATEST_VERSION_HEADER]
        with self.assertRaises(KeyError):
            response[AppVersionUpgrade.UPGRADE_DEADLINE_HEADER]

    @ddt.data(
        "edX/org.edx.mobile (5.1.1; OS Version 9.2 (Build 13C75))",
        "edX/org.edx.mobile (5.1.1.RC; OS Version 9.2 (Build 13C75))",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/5.1.1",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/5.1.1.RC",
    )
    def test_new_version_available(self, user_agent):
        fake_request = HttpRequest()
        fake_request.META['HTTP_USER_AGENT'] = user_agent
        self.assertIsNone(self.middleware.process_request(fake_request))
        fake_response = HttpResponse()
        response = self.middleware.process_response(fake_request, fake_response)
        self.assertEquals(200, response.status_code)
        self.assertEqual("6.6.6", response[AppVersionUpgrade.LATEST_VERSION_HEADER])
        with self.assertRaises(KeyError):
            response[AppVersionUpgrade.UPGRADE_DEADLINE_HEADER]

    @ddt.data(
        "edX/org.edx.mobile (1.0.1; OS Version 9.2 (Build 13C75))",
        "edX/org.edx.mobile (1.1.1; OS Version 9.2 (Build 13C75))",
        "edX/org.edx.mobile (2.0.5.RC; OS Version 9.2 (Build 13C75))",
        "edX/org.edx.mobile (2.2.2; OS Version 9.2 (Build 13C75))",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/1.0.1",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/1.1.1",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/2.0.5.RC",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/2.2.2",
    )
    def test_version_update_required(self, user_agent):
        fake_request = HttpRequest()
        fake_request.META['HTTP_USER_AGENT'] = user_agent
        result = self.middleware.process_request(fake_request)
        self.assertIsNotNone(result)
        response = self.middleware.process_response(fake_request, result)
        self.assertEquals(426, response.status_code)
        self.assertEqual("6.6.6", response[AppVersionUpgrade.LATEST_VERSION_HEADER])

    @ddt.data(
        "edX/org.edx.mobile (4.4.4; OS Version 9.2 (Build 13C75))",
        "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/4.4.4",
    )
    def test_version_update_available_with_deadline(self, user_agent):
        fake_request = HttpRequest()
        fake_request.META['HTTP_USER_AGENT'] = user_agent
        self.assertIsNone(self.middleware.process_request(fake_request))
        fake_response = HttpResponse()
        response = self.middleware.process_response(fake_request, fake_response)
        self.assertEquals(200, response.status_code)
        self.assertEqual("6.6.6", response[AppVersionUpgrade.LATEST_VERSION_HEADER])
        self.assertEqual('9000-01-01 00:00:00+00:00', response[AppVersionUpgrade.UPGRADE_DEADLINE_HEADER])
