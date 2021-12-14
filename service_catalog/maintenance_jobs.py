import logging
import os
from django.conf import settings
from service_catalog.models.documentation import Doc
from service_catalog.utils import get_images_link_from_markdown

logger = logging.getLogger(__name__)


def cleanup_ghost_docs_images(image_path=None):
    """
    Delete all images from Martor media folder that are not linked to any docs
    """
    if image_path is None:
        image_path = settings.MEDIA_ROOT + os.sep + settings.MARTOR_UPLOAD_PATH
    logger.debug(f"[cleanup_ghost_docs_images] media image path: {image_path}")
    docs = Doc.objects.all()
    list_of_media = []
    for doc in docs:
        list_of_media += get_images_link_from_markdown(doc.content)
    logger.debug(f"[cleanup_ghost_docs_images] list of used media: {list_of_media}")
    files = next(os.walk(image_path), (None, None, []))[2]
    logger.debug(f"[cleanup_ghost_docs_images] list of media files: {files}")
    delta = list(set(files) - set(list_of_media))
    for file in delta:
        logger.info(f"[cleanup_ghost_docs_images] Media deleted: {file}")
        os.remove(image_path + os.sep + file)
    return delta
