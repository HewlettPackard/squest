from service_catalog.models import Doc
from service_catalog.utils import get_images_link_from_markdown


def cleanup_ghost_docs_images():
    """
    Delete all images from Martor media folder that are not linked to any docs
    """
    docs = Doc.objects.all()
    list_of_media = []
    for doc in docs:
        list_of_media += get_images_link_from_markdown(doc.content)

    import os
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk("media/doc_images/") for f in filenames]
    delta = list(set(files) - set(list_of_media))
    for file in delta:
        print(f"Media deleted: {file}")
        os.remove(file)
