"""
Platform related operations for Mobile APP
"""
import abc
import re
from mobile_api.models import AppVersionConfig


class MobilePlatform(object):
    """
    MobilePlatform class creates an instance of platform based on user agent and supports platform
    related operations
    """
    __metaclass__ = abc.ABCMeta

    name = None
    version = None

    @classmethod
    def create_instance(cls, user_agent, user_agent_regex):
        """ Returns Android platform instance if user_agent matches with USER_AGENT_REGEX for Android """
        match = re.search(user_agent_regex, user_agent)
        if match:
            platform = cls()
            platform.set_version(match.group('version'))
            return platform

    def set_version(self, version):
        """ sets user app version in platform instance """
        self.version = version

    @classmethod
    def get_instance(cls, user_agent):
        """
        It creates an instance of one of the supported mobile platforms (i.e. iOS, Android) by regex comparison
        of user-agent.

        Parameters:
            user_agent: user_agent of mbile app

        Returns:
            instance of one of the supported mobile platforms (i.e. iOS, Android)
        """
        class Ios(MobilePlatform):
            """ iOS platform """
            USER_AGENT_REGEX = (r'\((?P<version>[0-9]+.[0-9]+.[0-9]+(.[0-9a-zA-Z]*)?); OS Version [0-9.]+ '
                                r'\(Build [0-9a-zA-Z]*\)\)')
            name = AppVersionConfig.IOS

        class Android(MobilePlatform):
            """ Android platform """
            USER_AGENT_REGEX = (r'Dalvik/[.0-9]+ \(Linux; U; Android [.0-9]+; (.*) Build/[0-9a-zA-Z]*\) '
                                r'(.*)/(?P<version>[0-9]+.[0-9]+.[0-9]+(.[0-9a-zA-Z]*)?)')
            name = AppVersionConfig.ANDROID

        # a list of all supported mobile platforms
        PLATFORM_CLASSES = [Ios, Android]  # pylint: disable=invalid-name
        for subclass in PLATFORM_CLASSES:
            instance = subclass.create_instance(user_agent, subclass.USER_AGENT_REGEX)
            if instance:
                return instance
