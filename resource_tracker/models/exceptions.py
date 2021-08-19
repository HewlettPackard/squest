class ExceptionResourceTracker:
    class AttributeAlreadyExist(Exception):
        def __init__(self, resource_group_name, attribute_name):
            super().__init__(f"Attribute {attribute_name} already exist in {resource_group_name}")
