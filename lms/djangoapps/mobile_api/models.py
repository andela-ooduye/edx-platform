"""
ConfigurationModel for the mobile_api djangoapp.
"""
from django.db.models.fields import TextField, DateTimeField, CharField, BooleanField, IntegerField
from config_models.models import ConfigurationModel, cache


class MobileApiConfig(ConfigurationModel):
    """
    Configuration for the video upload feature.

    The order in which the comma-separated list of names of profiles are given
    is in priority order.
    """
    video_profiles = TextField(
        blank=True,
        help_text="A comma-separated list of names of profiles to include for videos returned from the mobile API."
    )

    @classmethod
    def get_video_profiles(cls):
        """
        Get the list of profiles in priority order when requesting from VAL
        """
        return [profile.strip() for profile in cls.current().video_profiles.split(",") if profile]


class AppVersionConfig(ConfigurationModel):  # pylint: disable=model-missing-unicode
    """
    Configuration for mobile app versions available.
    """
    IOS = "ios"
    ANDROID = "android"
    PLATFORM = (
        (IOS, "iOS"),
        (ANDROID, "Android"),
    )
    KEY_FIELDS = ('platform', 'version')  # combination of mobile platform and version is unique
    platform = CharField(max_length=50, choices=PLATFORM, blank=False)
    version = CharField(max_length=50, blank=False)
    major_version = IntegerField()
    minor_version = IntegerField()
    patch_version = IntegerField()
    expire_at = DateTimeField(null=True, blank=True, verbose_name="Last Supported Date")

    class Meta:
        ordering = ['major_version', 'minor_version', 'patch_version']

    @classmethod
    def cache_key_name(cls, *args):
        """ Return the name of the key to use to cache all versions configuration against platform """
        return u'configuration/{}/current/{}'.format(cls.__name__, u'_'.join(unicode(arg) for arg in args))

    @classmethod
    def latest_version(cls, platform):
        """ return latest supported version for a platform"""
        cached = cache.get(cls.cache_key_name(platform, 'latest_version'))
        if cached:
            return cached

        active_configs = cls.objects.current_set().filter(platform=platform, enabled=True).reverse()
        if active_configs:
            latest_version = active_configs[0].version
            cache.set(
                cls.cache_key_name(platform, 'latest_version'),
                latest_version,
                ConfigurationModel.cache_timeout
            )
            return latest_version

    @classmethod
    def last_supported_date(cls, platform, version):
        """ returns date when version will get expired """
        cached = cache.get(cls.cache_key_name(platform, version, 'last_supported_date'))
        if cached:
            return cached

        active_configs = cls.objects.current_set().filter(platform=platform, enabled=True)
        for config in active_configs:
            if config.version >= version and config.expire_at:
                cache.set(
                    cls.cache_key_name(platform, version, 'last_supported_date'),
                    config.expire_at,
                    ConfigurationModel.cache_timeout
                )
                return config.expire_at

    def save(self, *args, **kwargs):
        """
        clear the cached value when saving a new configuration entry
        """
        cache.delete(AppVersionConfig.cache_key_name(self.platform, 'latest_version'))
        cache.delete(AppVersionConfig.cache_key_name(self.platform, self.version, 'last_supported_date'))
        parsed_version = tuple(map(int, (self.version.split(".")[:3])))
        self.major_version = parsed_version[0]
        self.minor_version = parsed_version[1]
        self.patch_version = parsed_version[2]
        super(AppVersionConfig, self).save(*args, **kwargs)
