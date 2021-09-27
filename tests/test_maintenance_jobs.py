import os
import shutil

from django.core.files import File

from django.conf import settings
from service_catalog.maintenance_jobs import cleanup_ghost_docs_images
from service_catalog.models import Doc
from tests.test_service_catalog.base import BaseTest


class TestMaintenanceJob(BaseTest):

    def setUp(self):
        super(TestMaintenanceJob, self).setUp()
        self.test_root = os.path.abspath(os.path.dirname(__file__))
        self._old_MEDIA_ROOT = settings.MEDIA_ROOT
        # override MEDIA_ROOT for this test
        settings.MEDIA_ROOT = os.path.join(self.test_root, 'media')

    def tearDown(self):
        # Cleanup path
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        # reset MEDIA_ROOT
        settings.MEDIA_ROOT = self._old_MEDIA_ROOT

    def test_cleanup_ghost_docs_images(self):
        doc_image_path = settings.MEDIA_ROOT + os.sep + settings.MARTOR_UPLOAD_PATH
        from pathlib import Path
        path = Path(doc_image_path)
        path.mkdir(parents=True, exist_ok=True)
        # create a media
        with open(doc_image_path + "/to_be_kept.jpg", 'w') as f:
            to_be_kept = File(f)
            to_be_kept.write("to_be_kept")
        with open(doc_image_path + "/to_be_deleted.jpg", 'w') as f:
            to_be_kept = File(f)
            to_be_kept.write("to_be_deleted")

        content = """
# Delete Images test
![image](/media/doc_images/uploads/to_be_kept.jpg)
"""
        # create a doc
        Doc.objects.create(title="test doc", content=content)
        deleted_media_list = cleanup_ghost_docs_images(image_path=doc_image_path)
        expected_list_of_deleted_files = ["to_be_deleted.jpg"]
        self.assertEquals(deleted_media_list, expected_list_of_deleted_files)
