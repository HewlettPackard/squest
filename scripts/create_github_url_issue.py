import urllib.parse as urlparse
from urllib.parse import urlencode


def create_url_for_github_issue(github_endpoint_issue, title, body):
    url = github_endpoint_issue
    params = {'title': title, 'body': body}
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)

    url_to_open_issue = urlparse.urlunparse(url_parts)[:2000]  # URL should not exceed 2000 characters
    return url_to_open_issue


github_endpoint_new_issue = "https://github.com/HewlettPackard/squest/issues/new?"
title = 'Templated Github issue'
body = '''Instance <a href="https://mysquest.net/ui/service_catalog/instance/JINJA_REPLACE/">JINJA_REPLACE</a>'''
my_link = create_url_for_github_issue(github_endpoint_new_issue, title, body)
print(my_link)

print("Replace all 'JINJA_REPLACE' with the jinja code you need. E.g '{{ instance.name }}'")
