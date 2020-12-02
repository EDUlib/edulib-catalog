"""
Django settings for FUN-MOOC project.
"""
import json
import os

from django.utils.translation import gettext_lazy as _

# pylint: disable=ungrouped-imports
import sentry_sdk
from configurations import Configuration, values
from richie.apps.courses.settings.mixins import RichieCoursesConfigurationMixin
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join("/", "data")


def get_release():
    """Get the current release of the application.

    By release, we mean the release from the version.json file à la Mozilla [1]
    (if any). If this file has not been found, it defaults to "NA".

    [1]
    https://github.com/mozilla-services/Dockerflow/blob/master/docs/version_object.md
    """
    # Try to get the current release from the version.json file generated by the
    # CI during the Docker image build
    try:
        with open(os.path.join(BASE_DIR, "version.json")) as version:
            return json.load(version)["version"]
    except FileNotFoundError:
        return "NA"  # Default: not available


class StyleguideMixin:
    """
    Theme styleguide reference

    Only used to build styleguide page without the need to hardcode properties
    and values into styleguide template.
    """

    STYLEGUIDE = {
        # Available font family names
        "fonts": ["hind", "montserrat"],
        # Named color palette
        "palette": [
            "black",
            "dark-grey",
            "charcoal",
            "slate-grey",
            "battleship-grey",
            "light-grey",
            "silver",
            "azure2",
            "smoke",
            "white",
            "denim",
            "firebrick6",
            "purplish-grey",
            "grey32",
            "grey59",
            "grey87",
            "indianred3",
            "midnightblue",
        ],
        # Available gradient background
        "gradient_colors": [
            "neutral-gradient",
            "light-gradient",
            "middle-gradient",
            "dark-gradient",
            "white-mask-gradient",
        ],
        # Available color schemes
        "schemes": [
            "primary",
            "secondary",
            "tertiary",
            "clear",
            "light",
            "lightest",
            "indianred3",
            "clear-red",
            "neutral-gradient",
            "light-gradient",
            "middle-gradient",
            "dark-gradient",
            "white-mask-gradient",
            "clouds",
            "transparent-clear",
            "transparent-darkest",
        ],
    }


class DRFMixin:
    """
    Django Rest Framework configuration mixin.
    NB: DRF picks its settings from the REST_FRAMEWORK namespace on the settings, hence
    the nesting of all our values inside that prop
    """

    REST_FRAMEWORK = {
        "ALLOWED_VERSIONS": ("1.0",),
        "DEFAULT_VERSION": "1.0",
        "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
        ),
    }


class Base(StyleguideMixin, DRFMixin, RichieCoursesConfigurationMixin, Configuration):
    """
    This is the base configuration every configuration (aka environnement) should inherit from. It
    is recommended to configure third-party applications by creating a configuration mixins in
    ./configurations and compose the Base configuration with those mixins.

    It depends on an environment variable that SHOULD be defined:

    * DJANGO_SECRET_KEY

    You may also want to override default configuration by setting the following environment
    variables:

    * DJANGO_SENTRY_DSN
    * RICHIE_ES_HOST
    * DB_NAME
    * DB_USER
    * DB_PASSWORD
    * DB_HOST
    * DB_PORT
    """

    DEBUG = False

    SITE_ID = 1

    # Security
    ALLOWED_HOSTS = values.ListValue([])
    SECRET_KEY = "ThisIsAnExampleKeyForDevPurposeOnly"  # nosec
    # System check reference:
    # https://docs.djangoproject.com/en/3.1/ref/checks/#security
    SILENCED_SYSTEM_CHECKS = values.ListValue(
        [
            # Allow the X_FRAME_OPTIONS to be set to "SAMEORIGIN"
            "security.W019"
        ]
    )
    # The X_FRAME_OPTIONS value should be set to "SAMEORIGIN" to display
    # DjangoCMS frontend admin frames. Dockerflow raises a system check security
    # warning with this setting, one should add "security.W019" to the
    # SILENCED_SYSTEM_CHECKS setting (see above).
    X_FRAME_OPTIONS = "SAMEORIGIN"

    # Application definition
    ROOT_URLCONF = "funmooc.urls"
    WSGI_APPLICATION = "funmooc.wsgi.application"

    # Database
    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DB_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value(
                "funmooc", environ_name="DB_NAME", environ_prefix=None
            ),
            "USER": values.Value("fun", environ_name="DB_USER", environ_prefix=None),
            "PASSWORD": values.Value(
                "pass", environ_name="DB_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "localhost", environ_name="DB_HOST", environ_prefix=None
            ),
            "PORT": values.Value(5432, environ_name="DB_PORT", environ_prefix=None),
        }
    }
    MIGRATION_MODULES = {}

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(DATA_DIR, "media")
    STATIC_ROOT = os.path.join(DATA_DIR, "static")

    # For static files, we want to use a backend that includes a hash in
    # the filename, that is calculated from the file content, so that browsers always
    # get the updated version of each file.
    STATICFILES_STORAGE = values.Value("base.storage.CDNManifestStaticFilesStorage")

    # Login/registration related settings
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"

    # AUTHENTICATION
    RICHIE_AUTHENTICATION_DELEGATION = {
        "BASE_URL": values.Value(
            "", environ_name="AUTHENTICATION_BASE_URL", environ_prefix=None
        ),
        "BACKEND": values.Value(
            "openedx-dogwood",
            environ_name="AUTHENTICATION_BACKEND",
            environ_prefix=None,
        ),
        # PROFILE_URLS are custom links to access to Auth profile views
        # from Richie. Link order will reflect the order of display in frontend.
        # (i) Info - {base_url} is AUTHENTICATION_DELEGATION.BASE_URL
        # (i) If you need to bind user data into href url, wrap the property between ()
        # e.g: for user.username = johndoe, /u/(username) will be /u/johndoe
        "PROFILE_URLS": values.ListValue(
            [
                {"label": _("Profile"), "href": "{base_url:s}/u/(username)"},
                {"label": _("Account"), "href": "{base_url:s}/account/settings"},
            ],
            environ_name="AUTHENTICATION_PROFILE_URLS",
            environ_prefix=None,
        ),
    }

    # LMS
    LMS_BACKENDS = [
    ]
    RICHIE_COURSE_RUN_SYNC_SECRETS = values.ListValue([])

    # Internationalization
    TIME_ZONE = "Europe/Paris"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

    # Templates
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "templates")],
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.template.context_processors.media",
                    "django.template.context_processors.csrf",
                    "django.template.context_processors.tz",
                    "sekizai.context_processors.sekizai",
                    "django.template.context_processors.static",
                    "cms.context_processors.cms_settings",
                    "richie.apps.core.context_processors.site_metas",
                ],
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        }
    ]

    MIDDLEWARE = (
        "richie.apps.core.cache.LimitBrowserCacheTTLHeaders",
        "cms.middleware.utils.ApphookReloadMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "dockerflow.django.middleware.DockerflowMiddleware",
        "cms.middleware.user.CurrentUserMiddleware",
        "cms.middleware.page.CurrentPageMiddleware",
        "cms.middleware.toolbar.ToolbarMiddleware",
        "cms.middleware.language.LanguageCookieMiddleware",
        "dj_pagination.middleware.PaginationMiddleware",
    )

    INSTALLED_APPS = (
        # Funmooc stuff
        "base",
        # Richie stuff
        "richie.apps.demo",
        "richie.apps.search",
        "richie.apps.courses",
        "richie.apps.core",
        "richie.plugins.glimpse",
        "richie.plugins.html_sitemap",
        "richie.plugins.large_banner",
        "richie.plugins.nesteditem",
        "richie.plugins.plain_text",
        "richie.plugins.section",
        "richie.plugins.simple_picture",
        "richie.plugins.simple_text_ckeditor",
        "richie",
        # Third party apps
        "dj_pagination",
        "dockerflow.django",
        "parler",
        "rest_framework",
        "storages",
        # Django-cms
        "djangocms_admin_style",
        "djangocms_googlemap",
        "djangocms_link",
        "djangocms_picture",
        "djangocms_text_ckeditor",
        "djangocms_video",
        "cms",
        "menus",
        "sekizai",
        "treebeard",
        "filer",
        "easy_thumbnails",
        # Django
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.admin",
        "django.contrib.sites",
        "django.contrib.sitemaps",
        "django.contrib.staticfiles",
        "django.contrib.messages",
    )

    #Plugin restrictions
    CMS_PLACEHOLDER_CONF = {
        # -- Static Placeholders
        # Footer
        "footer": {
            "name": _("Footer"),
            "plugins": ["NestedItemPlugin", "LinkPlugin"],
            "NestedItemPlugin": ["LinkPlugin"],
        },
        "static_blogpost_headline": {
            "name": _("Static headline"),
            "plugins": ["SectionPlugin", "CKEditorPlugin"],
            "child_classes": {"SectionPlugin": ["CKEditorPlugin"]},
        },
        # -- Page Placeholders
        # Homepage
        "richie/homepage.html maincontent": {
            "name": _("Main content"),
            "plugins": ["LargeBannerPlugin", "SectionPlugin"],
            "child_classes": {
                "SectionPlugin": [
                    "BlogPostPlugin",
                    "CategoryPlugin",
                    "CoursePlugin",
                    "CKEditorPlugin",
                    "GlimpsePlugin",
                    "LinkPlugin",
                    "NestedItemPlugin",
                    "OrganizationsByCategoryPlugin",
                    "OrganizationPlugin",
                    "PersonPlugin",
                    "ProgramPlugin",
                    "SectionPlugin",
                ],
                "NestedItemPlugin": ["CategoryPlugin"],
            },
        },
        # Single column page
        "richie/single_column.html maincontent": {
            "name": _("Main content"),
            "excluded_plugins": ["CKEditorPlugin", "GoogleMapPlugin"],
            "parent_classes": {
                "BlogPostPlugin": ["SectionPlugin"],
                "CategoryPlugin": ["SectionPlugin"],
                "CoursePlugin": ["SectionPlugin"],
                "GlimpsePlugin": ["SectionPlugin"],
                "OrganizationPlugin": ["SectionPlugin"],
                "OrganizationsByCategoryPlugin": ["SectionPlugin"],
                "PersonPlugin": ["SectionPlugin"],
                "ProgramPlugin": ["SectionPlugin"],
            },
            "child_classes": {
                "SectionPlugin": [
                    "BlogPostPlugin",
                    "CategoryPlugin",
                    "CoursePlugin",
                    "GlimpsePlugin",
                    "LinkPlugin",
                    "NestedItemPlugin",
                    "OrganizationsByCategoryPlugin",
                    "OrganizationPlugin",
                    "PersonPlugin",
                    "ProgramPlugin",
                ],
                "NestedItemPlugin": ["NestedItemPlugin", "LinkPlugin"],
            },
        },
        # Course detail
        "courses/cms/course_detail.html course_cover": {
            "name": _("Cover"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/course_detail.html course_introduction": {
            "name": _("Catch phrase"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        "courses/cms/course_detail.html course_teaser": {
            "name": _("Teaser"),
            "plugins": ["VideoPlayerPlugin", "SimplePicturePlugin"],
            "limits": {"VideoPlayerPlugin": 1, "SimplePicturePlugin": 1},
        },
        "courses/cms/course_detail.html course_description": {
            "name": _("About the course"),
            "plugins": ["CKEditorPlugin", "NestedItemPlugin", "SimplePicturePlugin"],
        },
        "courses/cms/course_detail.html course_skills": {
            "name": _("What you will learn"),
            "plugins": ["CKEditorPlugin"],
        },
        "courses/cms/course_detail.html course_format": {
            "name": _("Format"),
            "plugins": ["CKEditorPlugin"],
        },
        "courses/cms/course_detail.html course_prerequisites": {
            "name": _("Prerequisites"),
            "plugins": ["CKEditorPlugin"],
        },
        "courses/cms/course_detail.html course_team": {
            "name": _("Team"),
            "plugins": ["PersonPlugin"],
        },
        "courses/cms/course_detail.html course_plan": {
            "name": _("Plan"),
            "plugins": ["NestedItemPlugin"],
            "child_classes": {"NestedItemPlugin": ["NestedItemPlugin"]},
        },
        "courses/cms/course_detail.html course_information": {
            "name": _("Complementary information"),
            "plugins": ["SectionPlugin"],
            "parent_classes": {
                "CKEditorPlugin": ["SectionPlugin"],
                "SimplePicturePlugin": ["SectionPlugin"],
                "GlimpsePlugin": ["SectionPlugin"],
            },
            "child_classes": {
                "SectionPlugin": ["CKEditorPlugin", "SimplePicturePlugin", "GlimpsePlugin"]
            },
        },
        "courses/cms/course_detail.html course_more_information": {
            "name": _("Complementary information"),
            "plugins": ["SectionPlugin"],
            "parent_classes": {
                "CKEditorPlugin": ["SectionPlugin"],
                "SimplePicturePlugin": ["SectionPlugin"],
                "GlimpsePlugin": ["SectionPlugin"],
            },
            "child_classes": {
                "SectionPlugin": ["CKEditorPlugin", "SimplePicturePlugin", "GlimpsePlugin"]
            },
        },
        "courses/cms/course_detail.html course_license_content": {
            "name": _("License for the course content"),
            "plugins": ["LicencePlugin"],
            "limits": {"LicencePlugin": 1},
        },
        "courses/cms/course_detail.html course_license_participation": {
            "name": _("License for the content created by course participants"),
            "plugins": ["LicencePlugin"],
            "limits": {"LicencePlugin": 1},
        },
        "courses/cms/course_detail.html course_categories": {
            "name": _("Categories"),
            "plugins": ["CategoryPlugin"],
        },
        "courses/cms/course_detail.html course_icons": {
            "name": _("Icon"),
            "plugins": ["CategoryPlugin"],
            "limits": {"CategoryPlugin": 1},
        },
        "courses/cms/course_detail.html course_organizations": {
            "name": _("Organizations"),
            "plugins": ["OrganizationPlugin"],
        },
        "courses/cms/course_detail.html course_assessment": {
            "name": _("Assessment and Certification"),
            "plugins": ["CKEditorPlugin"],
        },
        # Organization detail
        "courses/cms/organization_detail.html banner": {
            "name": _("Banner"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/organization_detail.html logo": {
            "name": _("Logo"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/organization_detail.html categories": {
            "name": _("Categories"),
            "plugins": ["CategoryPlugin"],
        },
        "courses/cms/organization_detail.html description": {
            "name": _("Description"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        # Category detail
        "courses/cms/category_detail.html banner": {
            "name": _("Banner"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/category_detail.html logo": {
            "name": _("Logo"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/category_detail.html icon": {
            "name": _("Icon"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/category_detail.html description": {
            "name": _("Description"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        # Person detail
        "courses/cms/person_detail.html categories": {
            "name": _("Categories"),
            "plugins": ["CategoryPlugin"],
        },
        "courses/cms/person_detail.html portrait": {
            "name": _("Portrait"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/person_detail.html bio": {
            "name": _("Bio"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        "courses/cms/person_detail.html maincontent": {
            "name": _("Main Content"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        "courses/cms/person_detail.html organizations": {
            "name": _("Organizations"),
            "plugins": ["OrganizationPlugin"],
        },
        # Blog page detail
        "courses/cms/blogpost_detail.html author": {
            "name": _("Author"),
            "plugins": ["PersonPlugin"],
            "limits": {"PersonPlugin": 1},
        },
        "courses/cms/blogpost_detail.html categories": {
            "name": _("Categories"),
            "plugins": ["CategoryPlugin"],
        },
        "courses/cms/blogpost_detail.html cover": {
            "name": _("Cover"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/blogpost_detail.html excerpt": {
            "name": _("Excerpt"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        "courses/cms/blogpost_detail.html body": {
            "name": _("Body"),
            "excluded_plugins": ["CKEditorPlugin", "GoogleMapPlugin"],
        },
        "courses/cms/blogpost_detail.html headline": {
            "name": _("Headline"),
            "plugins": ["SectionPlugin", "CKEditorPlugin"],
            "child_classes": {"SectionPlugin": ["CKEditorPlugin"]},
        },
        # Program page detail
        "courses/cms/program_detail.html program_cover": {
            "name": _("Cover"),
            "plugins": ["SimplePicturePlugin"],
            "limits": {"SimplePicturePlugin": 1},
        },
        "courses/cms/program_detail.html program_excerpt": {
            "name": _("Excerpt"),
            "plugins": ["CKEditorPlugin"],
            "limits": {"CKEditorPlugin": 1},
        },
        "courses/cms/program_detail.html program_body": {
            "name": _("Body"),
            "excluded_plugins": ["CKEditorPlugin", "GoogleMapPlugin"],
        },
        "courses/cms/program_detail.html program_courses": {
            "name": _("Courses"),
            "plugins": ["CoursePlugin"],
        },
        "courses/cms/program_list.html maincontent": {
            "name": _("Main content"),
            "plugins": ["SectionPlugin"],
            "child_classes": {
                "SectionPlugin": [
                    "BlogPostPlugin",
                    "CategoryPlugin",
                    "CoursePlugin",
                    "GlimpsePlugin",
                    "LinkPlugin",
                    "OrganizationPlugin",
                    "OrganizationsByCategoryPlugin",
                    "PersonPlugin",
                    "CKEditorPlugin",
                    "SectionPlugin",
                    "NestedItemPlugin",
                ],
                "NestedItemPlugin": ["CategoryPlugin"],
            },
        },
    }

    RICHIE_SIMPLETEXT_CONFIGURATION = [
    ]

    #Search
    RICHIE_FILTERS_CONFIGURATION = [
        (
            "richie.apps.search.filter_definitions.NestingWrapper",
            {
                "name": "course_runs",
                "filters": [
                    (
                        "richie.apps.search.filter_definitions.AvailabilityFilterDefinition",
                        {
                            "human_name": _("Availability"),
                            "is_drilldown": True,
                            "min_doc_count": 0,
                            "name": "availability",
                            "position": 0,
                        },
                    ),
                    (
                        "richie.apps.search.filter_definitions.LanguagesFilterDefinition",
                        {
                            "human_name": _("Languages"),
                            # There are too many available languages to show them all, all the time.
                            # Eg. 200 languages, 190+ of which will have 0 matching courses.
                            "min_doc_count": 1,
                            "name": "languages",
                            "position": 3,
                            "sorting": "count",
                        },
                    ),
                ],
            },
        ),
        (
            "richie.apps.search.filter_definitions.IndexableMPTTFilterDefinition",
            {
                "human_name": _("Subjects"),
                "is_autocompletable": True,
                "is_searchable": True,
                "min_doc_count": 0,
                "name": "subjects",
                "position": 1,
                "reverse_id": "subjects",
                "term": "categories",
            },
        ),
        (
            "richie.apps.search.filter_definitions.IndexableMPTTFilterDefinition",
            {
                "human_name": _("Host"),
                "is_autocompletable": True,
                "is_searchable": True,
                "min_doc_count": 0,
                "name": "host",
                "position": 4,
                "reverse_id": "host",
                "term": "categories",
            },
        ),
        (
            "richie.apps.search.filter_definitions.IndexableMPTTFilterDefinition",
            {
                "human_name": _("Certificate"),
                "is_autocompletable": True,
                "is_searchable": True,
                "min_doc_count": 0,
                "name": "certificate",
                "position": 5,
                "reverse_id": "certificate",
                "term": "categories",
            },
        ),
        (
            "richie.apps.search.filter_definitions.IndexableMPTTFilterDefinition",
            {
                "human_name": _("Organizations"),
                "is_autocompletable": True,
                "is_searchable": True,
                "min_doc_count": 0,
                "name": "organizations",
                "position": 2,
                "reverse_id": "organizations",
            },
        ),
        (
            "richie.apps.search.filter_definitions.IndexableFilterDefinition",
            {
                "human_name": _("Persons"),
                "is_autocompletable": True,
                "is_searchable": True,
                "min_doc_count": 0,
                "name": "persons",
                "position": 6,
                "reverse_id": "persons",
            },
        ),
    ]

    # Languages
    # - Django
    LANGUAGE_CODE = "fr"

    # Careful! Languages should be ordered by priority, as this tuple is used to get
    # fallback/default languages throughout the app.
    # Use "en" as default as it is the language that is most likely to be spoken by any visitor
    # when their preferred language, whatever it is, is unavailable
    LANGUAGES = (("en", _("English")), ("fr", _("French")))

    # - Django CMS
    CMS_LANGUAGES = {
        "default": {
            "public": True,
            "hide_untranslated": False,
            "redirect_on_fallback": True,
            "fallbacks": ["en", "fr"],
        },
        1: [
            {
                "public": True,
                "code": "en",
                "hide_untranslated": False,
                "name": _("English"),
                "fallbacks": ["fr"],
                "redirect_on_fallback": True,
            },
            {
                "public": True,
                "code": "fr",
                "hide_untranslated": False,
                "name": _("French"),
                "fallbacks": ["en"],
                "redirect_on_fallback": True,
            },
        ],
    }

    # - Django Parler
    PARLER_LANGUAGES = CMS_LANGUAGES

    # Permisions
    # - Django CMS
    CMS_PERMISSION = True

    # - Django Filer
    FILER_ENABLE_PERMISSIONS = True
    FILER_IS_PUBLIC_DEFAULT = True

    # - Django Pagination
    PAGINATION_INVALID_PAGE_RAISES_404 = True
    PAGINATION_DEFAULT_WINDOW = 2
    PAGINATION_DEFAULT_MARGIN = 1

    # Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s "
                "%(process)d %(thread)d %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            }
        },
        "loggers": {
            "django.db.backends": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            }
        },
    }

    # Demo
    RICHIE_DEMO_SITE_DOMAIN = "localhost:8080"
    RICHIE_DEMO_FIXTURES_DIR = os.path.join(BASE_DIR, "base", "fixtures")

    # Elasticsearch
    RICHIE_ES_HOST = values.Value(
        "elasticsearch", environ_name="RICHIE_ES_HOST", environ_prefix=None
    )
    RICHIE_ES_INDICES_PREFIX = values.Value(
        default="richie", environ_name="RICHIE_ES_INDICES_PREFIX", environ_prefix=None
    )

    # Cache
    CACHES = values.DictValue(
        {
            "default": {
                "BACKEND": values.Value(
                    "django_redis.cache.RedisCache",
                    environ_name="CACHE_DEFAULT_BACKEND",
                    environ_prefix=None,
                ),
                "LOCATION": values.Value(
                    "mymaster/redis-sentinel:26379,redis-sentinel:26379/0",
                    environ_name="CACHE_DEFAULT_LOCATION",
                    environ_prefix=None,
                ),
                "OPTIONS": values.DictValue(
                    {"CLIENT_CLASS": "richie.apps.core.cache.SentinelClient"},
                    environ_name="CACHE_DEFAULT_OPTIONS",
                    environ_prefix=None,
                ),
                "TIMEOUT": values.IntegerValue(
                    300, environ_name="CACHE_DEFAULT_TIMEOUT", environ_prefix=None
                ),
            }
        }
    )

    # For more details about CMS_CACHE_DURATION, see :
    # http://docs.django-cms.org/en/latest/reference/configuration.html#cms-cache-durations
    CMS_CACHE_DURATIONS = values.DictValue(
        {"menus": 3600, "content": 86400, "permissions": 86400}
    )
    MAX_BROWSER_CACHE_TTL = 600

    # Sessions
    SESSION_ENGINE = values.Value("django.contrib.sessions.backends.cache")

    # Sentry
    SENTRY_DSN = values.Value(None, environ_name="SENTRY_DSN")

    # pylint: disable=invalid-name
    @property
    def ENVIRONMENT(self):
        """Environment in which the application is launched."""
        return self.__class__.__name__.lower()

    # pylint: disable=invalid-name
    @property
    def RELEASE(self):
        """
        Return the release information.

        Delegate to the module function to enable easier testing.
        """
        return get_release()

    # pylint: disable=invalid-name
    @property
    def CMS_CACHE_PREFIX(self):
        """
        Set cache prefix specific to release so existing cache is invalidated for new deployments.
        """
        return f"cms_{get_release():s}_"

    @classmethod
    def post_setup(cls):
        """Post setup configuration.
        This is the place where you can configure settings that require other
        settings to be loaded.
        """
        super().post_setup()

        # The SENTRY_DSN setting should be available to activate sentry for an environment
        if cls.SENTRY_DSN is not None:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                environment=cls.__name__.lower(),
                release=get_release(),
                integrations=[DjangoIntegration()],
            )
            with sentry_sdk.configure_scope() as scope:
                scope.set_extra("application", "backend")


class Development(Base):
    """
    Development environment settings

    We set DEBUG to True and configure the server to respond from all hosts.
    """

    DEBUG = True
    ALLOWED_HOSTS = ["*"]

    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


class Test(Base):
    """Test environment settings"""


class ContinuousIntegration(Test):
    """
    Continous Integration environment settings

    nota bene: it should inherit from the Test environment.
    """


class Production(Base):
    """Production environment settings

    You must define the DJANGO_ALLOWED_HOSTS environment variable in Production
    configuration (and derived configurations):

    DJANGO_ALLOWED_HOSTS="foo.com,foo.fr"
    """

    # Security
    SECRET_KEY = values.SecretValue()
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True

    DEFAULT_FILE_STORAGE = "base.storage.MediaStorage"
    AWS_DEFAULT_ACL = None
    AWS_LOCATION = "media"

    AWS_ACCESS_KEY_ID = values.SecretValue()
    AWS_SECRET_ACCESS_KEY = values.SecretValue()

    AWS_S3_OBJECT_PARAMETERS = {
        "Expires": "Thu, 31 Dec 2099 20:00:00 GMT",
        "CacheControl": "max-age=94608000",
    }

    AWS_S3_REGION_NAME = values.Value("eu-west-1")

    AWS_MEDIA_BUCKET_NAME = values.Value("production-funmooc-media")

    # CDN domain for static/media urls. It is passed to the frontend to load built chunks
    CDN_DOMAIN = values.Value()

    @property
    def TEXT_CKEDITOR_BASE_PATH(self):
        """Configure CKEditor with an absolute url as base path to point to CloudFront."""
        return "//{!s}/static/djangocms_text_ckeditor/ckeditor/".format(self.CDN_DOMAIN)


class Feature(Production):
    """
    Feature environment settings

    nota bene: it should inherit from the Production environment.
    """

    AWS_MEDIA_BUCKET_NAME = values.Value("feature-funmooc-media")


class Staging(Production):
    """
    Staging environment settings

    nota bene: it should inherit from the Production environment.
    """

    AWS_MEDIA_BUCKET_NAME = values.Value("staging-funmooc-media")


class PreProduction(Production):
    """
    Pre-production environment settings

    nota bene: it should inherit from the Production environment.
    """

    AWS_MEDIA_BUCKET_NAME = values.Value("preprod-funmooc-media")
