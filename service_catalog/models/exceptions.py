class ExceptionServiceCatalog:
    class JobTemplateNotFound(Exception):
        def __init__(self, job_template_id, tower_name):
            super().__init__(f"Job Template ID {job_template_id} was not found in the server {tower_name}")
