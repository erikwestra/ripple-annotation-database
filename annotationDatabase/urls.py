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
    url(r'^admin/user/', include('annotationDatabase.authentication.urls')),
)

# Include our admin urls.

urlpatterns += patterns('',
    url(r'admin/', include("annotationDatabase.admin.urls")),
)

# Include our public urls.

urlpatterns += patterns('',
    url(r'public/', include("annotationDatabase.public.urls")),
)

# Include our public admin urls.

urlpatterns += patterns('',
    url(r'admin/public/', include("annotationDatabase.public.admin.urls")),
)

# Finally, redirect the top-level URL to our public interface.

urlpatterns += patterns('',
    url(r'^$', RedirectView.as_view(url="/public")),
)

