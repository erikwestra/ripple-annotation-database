""" annotationDatabase.admin.menus

    This module defines a helper function which builds the menu bar to include
    at the top of each admin page.
"""
from annotationDatabase.authentication import auth_controller

#############################################################################

def get_admin_menus(request):
    """ Return the menus to use in an admin page.

        The returned value should be passed to a Django template in a template
        variable named 'menus'.  If this template is based on shared/base.html,
        the menus will be created automatically.
    """
    annotation_menu_items = [
        ("Add Annotations",          "/admin/annotations/add"),
        ("Upload Annotations",       "/admin/annotations/upload"),
        ("View Annnotation Batches", "/admin/annotations/view"),
        ("------------------------", None),
        ("Search",                   "/admin/search"),
    ]

    template_menu_items = [
        ("View Annotation Templates",  "/admin/templates"),
        ("Upload Annotation Template", "/admin/templates/upload"),
    ]

    admin_menu_items = []
    if auth_controller.is_admin(request):
        admin_menu_items.append(("Add/Edit Administrators",
                                 auth_controller.get_user_admin_url()))
    admin_menu_items.append(("Add/Edit Client Systems", "/admin/clients"))

    user_menu_items = [
        ("Change Password", auth_controller.get_change_password_url()),
        ("Log Out",         auth_controller.get_logout_url()),
    ]

    menus = []
    menus.append({'title' : "Annotations",
                  'items' : annotation_menu_items})
    menus.append({'title' : "Templates",
                  'items' : template_menu_items})
    menus.append({'title' : "Admin",
                  'items' : admin_menu_items})
    menus.append({'title' : auth_controller.get_username(request),
                  'items' : user_menu_items})

    return menus

