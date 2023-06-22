from django.contrib.auth.backends import BaseBackend

from service_catalog.models import Instance, Request, Support


class MagicAdminBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # return True
        print(f"has perm called for user_obj={user_obj},perm={perm},obj={obj}")
        #
        # if obj == None:
        #     return False
        #     print(f"has perm with no answer for user_obj={user_obj},perm={perm},obj={obj}")

        if isinstance(obj, Instance):
            if perm == "service_catalog.view_instance":
                return False

        #     return False
        # elif isinstance(obj, Request):
        #     return user_obj.has_perm(perm="service_catalog.view_instance", obj=obj.instance)
        # elif isinstance(obj, Support):
        #     return user_obj.has_perm(perm=perm, obj=obj.instance)
        # else:
        #     print(f"has perm with no answer(else) for user_obj={user_obj},perm={perm},obj={obj}")
        #     return False
        # return False
