"""
tests for app version configuration model
"""
from datetime import datetime
import ddt
from django.test import TestCase
from pytz import UTC
from mobile_api.models import AppVersionConfig


@ddt.ddt
class TestAppVersionConfigModel(TestCase):
    """ Tests for app version configuration model """
    def setUp(self):
        super(TestAppVersionConfigModel, self).setUp()
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
        AppVersionConfig(platform="android", version="8.8.8", expire_at=None, enabled=True).save()

    @ddt.data(('ios', '6.6.6'), ('android', '8.8.8'))
    @ddt.unpack
    def test_latest_version(self, platform, latest_version):
         self.assertEqual(latest_version, AppVersionConfig.latest_version(platform))

    @ddt.data(
        ('ios', '4.4.4', datetime(9000, 1, 1, tzinfo=UTC)),
        ('ios', '6.6.6', None),
        ("android", '4.4.4', datetime(9000, 1, 1, tzinfo=UTC)),
        ('android', '8.8.8', None)
    )
    @ddt.unpack
    def test_last_supported_date(self, platform, version, last_supported_date):
         self.assertEqual(last_supported_date, AppVersionConfig.last_supported_date(platform, version))
