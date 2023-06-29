from copy import copy
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base import BaseTest


class ServiceCreateTestCase(BaseTest):

    def setUp(self):
        super(ServiceCreateTestCase, self).setUp()
        self.url = reverse('service_catalog:create_service')

    def test_create_service(self):
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "job_template_timeout": 60,
        }
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        number_service_before = copy(Service.objects.all().count())
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_service_before + 1,
                          Service.objects.all().count())

    def test_create_service_with_image(self):
        im = Image.new(mode='RGB', size=(200, 200))  # create a new image using PIL
        im_io = BytesIO()  # a BytesIO object for saving image
        im.save(im_io, 'JPEG')  # save the image to im_io
        im_io.seek(0)  # seek to the beginning
        image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', len(im_io.getvalue()), None
        )
        data = {
            "name": "new_service_with_image",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "job_template_timeout": 60,
            "image": image
        }
        number_service_before = Service.objects.all().count()
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_service_before + 1,
                          Service.objects.all().count())

        new_service_with_image = Service.objects.get(name="new_service_with_image")
        try:
            self.assertIsNotNone(new_service_with_image.image.file)
        except ValueError:
            self.fail("Image not set")
        # cleanup image after the test
        new_service_with_image.image.delete()
