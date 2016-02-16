"""
tests for platform against mobile app request
"""
from datetime import datetime
import ddt
from django.test import TestCase
from pytz import UTC
from mobile_api.mobile_platform import MobilePlatform
from mobile_api.models import AppVersionConfig


@ddt.ddt
class TestMobilePlatform(TestCase):
    """ Tests for platform against mobile app request """
    def setUp(self):
        super(TestMobilePlatform, self).setUp()
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
        ("edX/org.edx.mobile (1.1.1; OS Version 9.2 (Build 13C75))", AppVersionConfig.IOS, "1.1.1"),
        ("edX/org.edx.mobile (2.2.2; OS Version 9.2 (Build 13C75))", AppVersionConfig.IOS, "2.2.2"),
        ("edX/org.edx.mobile (3.3.3; OS Version 9.2 (Build 13C75))", AppVersionConfig.IOS, "3.3.3"),
        (
            "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/1.1.1",
            AppVersionConfig.ANDROID,
            "1.1.1"
        ),
        (
            "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/2.2.2",
            AppVersionConfig.ANDROID,
            "2.2.2"
        ),
        (
            "Dalvik/2.1.0 (Linux; U; Android 5.1; Nexus 5 Build/LMY47I) edX/org.edx.mobile/3.3.3",
            AppVersionConfig.ANDROID,
            "3.3.3"
        ),
    )
    @ddt.unpack
    def test_platform_instance(self, user_agent, platform_name, version):
        platform = MobilePlatform.get_instance(user_agent)
        self.assertEqual(platform_name, platform.name)
        self.assertEqual(version, platform.version)
