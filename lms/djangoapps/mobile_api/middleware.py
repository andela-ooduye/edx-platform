"""
Middleware for Mobile APIs
"""
from datetime import datetime
from django.core.cache import cache
from django.http import HttpResponse
from pytz import UTC
from mobile_api.mobile_platform import MobilePlatform
from mobile_api.models import AppVersionConfig
from mobile_api.utils import parsed_version
from openedx.core.lib.mobile_utils import is_request_from_mobile_app
from request_cache.middleware import RequestCache


class AppVersionUpgrade(object):
    """
    Middleware class to keep track of mobile application version being used
    """
    LATEST_VERSION_HEADER = 'EDX-APP-LATEST-VERSION'
    UPGRADE_DEADLINE_HEADER = 'EDX-APP-UPGRADE-DATE'

    def process_request(self, request):
        """
        raises HTTP Upgrade Require error if request is from mobile native app and
        user app version is no longer supported
        """
        user_agent = request.META.get('HTTP_USER_AGENT')
        last_supported_date = self.get_last_supported_date(request, user_agent)
        if last_supported_date:
            if datetime.now().replace(tzinfo=UTC) > last_supported_date:
                return HttpResponse(status=426)
            else:
                cache.set(
                    self.get_cache_key_name(user_agent, self.UPGRADE_DEADLINE_HEADER),
                    last_supported_date,
                    3600
                )
                RequestCache.get_request_cache().data[self.UPGRADE_DEADLINE_HEADER] = last_supported_date

    def process_response(self, _request, response):
        """
        If request is from mobile native app, then add headers to response;
        1. EDX-APP-LATEST-VERSION; if user app version < latest available version
        2. EDX-APP-UPGRADE-DATE; if user app version < min supported version and timestamp < deadline to upgrade
        """
        user_agent = _request.META.get('HTTP_USER_AGENT')
        request_cache_dict = RequestCache.get_request_cache().data
        upgrade_deadline = (request_cache_dict[self.UPGRADE_DEADLINE_HEADER]
                            if self.UPGRADE_DEADLINE_HEADER in request_cache_dict else None)
        if upgrade_deadline:
            response[self.UPGRADE_DEADLINE_HEADER] = upgrade_deadline
        if is_request_from_mobile_app(_request):
            platform = MobilePlatform.get_instance(user_agent)
            if platform:
                latest_version = self.get_latest_version(user_agent, platform.name)
                if latest_version and parsed_version(platform.version) < parsed_version(latest_version):
                    response[self.LATEST_VERSION_HEADER] = latest_version
        return response

    def get_cache_key_name(self, user_agent, field):
        """ get key name to use to cache any property against user agent """
        return "{}_{}".format(user_agent, field)

    def get_latest_version(self, user_agent, platform):
        """ get latest version available of app for platform """
        latest_version = cache.get(self.get_cache_key_name(user_agent, self.LATEST_VERSION_HEADER))
        if not latest_version:
            latest_version = AppVersionConfig.latest_version(platform)
            if latest_version:
                cache.set(self.get_cache_key_name(user_agent, self.LATEST_VERSION_HEADER), latest_version, 3600)
        return latest_version

    def get_last_supported_date(self, request, user_agent):
        """ get expiry date of app version for a platform """
        last_supported_date = cache.get(self.get_cache_key_name(user_agent, self.UPGRADE_DEADLINE_HEADER))
        if not last_supported_date and is_request_from_mobile_app(request):
            platform = MobilePlatform.get_instance(user_agent)
            if platform:
                last_supported_date = AppVersionConfig.last_supported_date(platform.name, platform.version)
        return last_supported_date
