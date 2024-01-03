from service_catalog.models import Doc
from tests.setup import SetupInstance


class TestDoc(SetupInstance):

    def test_render(self):
        # no instance, render return content
        new_doc = Doc.objects.create(title="test", content="test")
        self.assertEqual(new_doc.render(), "test")

        # with an instance with use the templating
        self.instance_1_org1.spec["dns"] = "name.domain.local"
        self.instance_1_org1.save()
        new_doc.content = "test {{ instance.spec.dns }}"
        new_doc.save()
        self.assertEqual(new_doc.render(self.instance_1_org1), "test name.domain.local")
