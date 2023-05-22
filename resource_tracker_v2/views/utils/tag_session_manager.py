import logging

from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def tag_session_manager(request):
    # keys in session
    tag_session_key = f'{request.path}__tag'
    tag_filter_type_session_key = f'{request.path}__tag_filter_type'

    # values in session
    tags_from_session = request.session.get(tag_session_key, [])
    tag_filter_type_from_session = request.session.get(tag_filter_type_session_key, "OR")
    if not request.GET and (tags_from_session != [] or tag_filter_type_from_session != "OR"):
        logger.info(f"Using tags loaded from session: {tags_from_session}")
        string_tag = "?"
        for tag in tags_from_session:
            string_tag += f"tag={tag}&"
        string_tag += f"tag_filter_type={tag_filter_type_from_session}"
        return redirect(request.path + string_tag)
    tag_list = request.GET.getlist("tag", [])
    logger.info(f"Settings tags from URL in session: {tag_list}")
    request.session[tag_session_key] = tag_list
    request.session[tag_filter_type_session_key] = request.GET.get("tag_filter_type", "OR")
