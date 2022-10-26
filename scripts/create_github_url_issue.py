import urllib.parse as urlparse
from urllib.parse import urlencode


def create_url_for_github_issue(github_endpoint_issue, issue_title="", issue_body="", assignees_list="", labels_list="",
                                projects_list=""):
    url = github_endpoint_issue
    params = {'title': issue_title, 'body': issue_body, 'assignees': assignees_list, 'labels': labels_list,
              'projects': projects_list}
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)

    url_to_open_issue = urlparse.urlunparse(url_parts)[:2000]  # URL should not exceed 2000 characters
    return url_to_open_issue


if __name__ == '__main__':
    # Replace your-repository-path by your repository
    github_endpoint_new_issue = "https://github.com/<your-repository-path>/issues/new?"

    # example of title
    title = '#SQUEST_INSTANCE_ID - '

    # example of body
    body = \
'''# My Squest instance details (auto-generated do not edit)
Squest Instance: SQUEST_INSTANCE_NAME (<a href="https://squest.gre.hpecorp.net/ui/service_catalog/instance/SQUEST_INSTANCE_ID/">#SQUEST_INSTANCE_ID</a>)
# My issue

'''

    # assignee username list as string separated by comma
    assignees = "user1,user2"

    # label name list as string separated by comma
    labels = "label1,label2"

    # project path list as string separated by comma
    projects = "project_path_1/<PROJECT_ID_1>,project_path_2/<PROJECT_ID_2>"

    my_link = create_url_for_github_issue(github_endpoint_new_issue, title, body, assignees, labels, projects)

    # use replace for templatizing your link as you want with jinja
    my_link = my_link.replace('SQUEST_INSTANCE_NAME', '{{instance.name}}').replace('SQUEST_INSTANCE_ID', '{{instance.id}}')

    print(my_link)
