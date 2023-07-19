import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from Squest.utils.squest_views import SquestListView

logger = logging.getLogger(__name__)


class TagFilterListView(SquestListView):
    @property
    def tag_session_key(self):
        return f'{self.request.path}__tag'

    @property
    def tag_filter_type_session_key(self):
        return f'{self.request.path}__tag_filter_type'

    def dispatch(self, *args, **kwargs):
        tags_from_session = self.request.session.get(self.tag_session_key, [])
        tag_filter_type_from_session = self.request.session.get(self.tag_filter_type_session_key, "OR")
        if not self.request.GET and (tags_from_session != [] or tag_filter_type_from_session != "OR"):
            logger.info(f"Using tags loaded from session: {tags_from_session}")
            string_tag = "?"
            for tag in tags_from_session:
                string_tag += f"tag={tag}&"
            string_tag += f"tag_filter_type={tag_filter_type_from_session}"
            return redirect(self.request.path + string_tag)
        return super(TagFilterListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.GET:
            tag_list = self.request.GET.getlist("tag")
            logger.info(f"Settings tags from URL in session: {tag_list}")
            self.request.session[self.tag_session_key] = tag_list
            self.request.session[self.tag_filter_type_session_key] = self.request.GET.get("tag_filter_type", "OR")
        return super(TagFilterListView, self).get_queryset()
