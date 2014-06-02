""" annotationDatabase.urls

    This module defines the top-level URL configuration for the Ripple
    Annotation Database.
"""
from django.conf          import settings
from django.conf.urls     import patterns, include, url
from django.views.generic import RedirectView

#############################################################################

urlpatterns = []

# Include our API urls.

urlpatterns += patterns('',
    url(r'', include("annotationDatabase.api.urls")),
)

# Include the authentication application's urls.

urlpatterns += patterns('',
    url(r'^authentication/', include('annotationDatabase.authentication.urls')),
)

# Include our admin urls.

urlpatterns += patterns('',
    url(r'^admin/', include("annotationDatabase.admin.urls")),
)

# Include our public urls.

urlpatterns += patterns('',
    url(r'^public/', include("annotationDatabase.public.urls")),
)

# Redirect the top-level URL to our public interface.

urlpatterns += patterns('',
    url(r'^$', RedirectView.as_view(url="/public")),
)

# If we've been configured to do so, serve our static files:

if settings.SERVE_STATIC_MEDIA:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root' : settings.STATICFILES_DIRS[0],
                 'show_indexes'  : True}),
    )

