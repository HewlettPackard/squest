from django import template

register = template.Library()


@register.simple_tag
def app_version():
    """
    Return Squest version as listed in `__version__` in `init.py` of settings package
    """
    import git
    from Squest.version import __version__
    repo = git.Repo(search_parent_directories=True)
    sha = str(repo.head.object.hexsha)[0:6]
    version = f"{__version__} - {sha}"
    return version
