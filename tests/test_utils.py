import unittest
from unittest import mock

from service_catalog.utils import str_to_bool, get_mysql_dump_major_version, \
    get_celery_crontab_parameters_from_crontab_line, get_images_link_from_markdown


class TestUtils(unittest.TestCase):

    def test_str_to_bool(self):
        self.assertTrue(str_to_bool("True"))
        self.assertTrue(str_to_bool("true"))
        self.assertTrue(str_to_bool(True))
        self.assertTrue(str_to_bool(1))
        self.assertTrue(str_to_bool("1"))
        self.assertFalse(str_to_bool("False"))
        self.assertFalse(str_to_bool("false"))
        self.assertFalse(str_to_bool(False))
        self.assertFalse(str_to_bool(0))
        self.assertFalse(str_to_bool("0"))

    @mock.patch('os.popen')
    def test_get_mysql_dump_major_version(self, mock_os_popen):
        map_test = {
            "mysqldump  Ver 8.0.26-0ubuntu0.20.04.2 for Linux on x86_64 ((Ubuntu))": 8,  # Ubuntu 20.04
            "mysqldump  Ver 10.19 Distrib 10.5.11-MariaDB, for debian-linux-gnu (x86_64)": 10,  # Debian Bullseye
            "mysqldump  Ver 10.19 Distrib 10.3.29-MariaDB, for debian-linux-gnu (x86_64)": 10,  # Debian Buster
            "mysqldump  Ver 12": 12,
            "mysqldump  Ver 101": 101,
            "other": None
        }

        for version_output, expected_result in map_test.items():
            process_mock = mock.Mock()
            attrs = {'read.return_value': version_output}
            process_mock.configure_mock(**attrs)
            mock_os_popen.return_value = process_mock
            self.assertEquals(get_mysql_dump_major_version(), expected_result)

    def test_get_celery_crontab_parameters_from_crontab_line(self):
        map_test = {
            "0 1 * * *": {
                "minute": "0",
                "hour": "1",
                "day_of_week": "*",
                "day_of_month": "*",
                "month_of_year": "*"
            },
            "1,4 1 * * *": {
                "minute": "1,4",
                "hour": "1",
                "day_of_week": "*",
                "day_of_month": "*",
                "month_of_year": "*"
            }
        }
        for crontab_line, expected_result in map_test.items():
            self.assertEquals(get_celery_crontab_parameters_from_crontab_line(crontab_line),
                              expected_result)

    def test_regex_for_media_cleanup(self):

        test_str = """
# Delete Images test
![Single picture on a line](/media/doc_images/uploads/to_be_deleted1.jpg)
TextBefore ![Single picture on a line with text before](/media/doc_images/uploads/to_be_deleted2.jpg)
![Single picture on a line with text after](/media/doc_images/uploads/to_be_deleted3.jpg) Text after
TextBefore ![Single picture on a line with text before and after](/notmedia/doc_images/uploads/non_deleted.jpg) Text after
![Single picture on a line on /media](/media/doc_images/google/doc_images/uploads/to_be_deleted4.jpg)
![First picture of the line](/media/doc_images/google/doc_images/uploads/to_be_deleted5.jpg)Random![Second picture of the line](/media/doc_images/google/doc_images/uploads/to_be_deleted6.jpg)
![Single picture on a line with space between] (/media/doc_images/uploads/picturelink.jpg)
![Single picture on a line with text between  ]eeeee(/media/doc_images/uploads/picturelink.jpg)
![Single picture on a line but not on /media/doc_images](/google/doc_images/uploads/picturelink.jpg) Text after
![Single picture on a line from google with /media/doc_images in path](https://google/media/doc_images/uploads/picturelink.jpg) 
"""
        list_expected = ['/media/doc_images/uploads/to_be_deleted1.jpg',
                         '/media/doc_images/uploads/to_be_deleted2.jpg',
                         '/media/doc_images/uploads/to_be_deleted3.jpg',
                         '/media/doc_images/google/doc_images/uploads/to_be_deleted4.jpg',
                         '/media/doc_images/google/doc_images/uploads/to_be_deleted5.jpg',
                         '/media/doc_images/google/doc_images/uploads/to_be_deleted6.jpg']

        list_of_media = get_images_link_from_markdown(test_str)
        self.assertListEqual(list_expected, list_of_media)
