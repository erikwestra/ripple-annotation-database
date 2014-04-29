""" annotationDatabase.urls

    This module defines the top-level URL configuration for the Ripple
    Annotation Database.
"""
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
    url(r'^web/user/', include('annotationDatabase.authentication.urls')),
)

# Include our web interface urls.

urlpatterns += patterns('',
    url(r'web/', include("annotationDatabase.web.urls")),
)

# Finally, redirect the top-level URL to our web interface.

urlpatterns += patterns('',
    url(r'^$', RedirectView.as_view(url="/web")),
)

