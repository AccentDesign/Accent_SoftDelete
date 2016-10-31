# helper to render a foreign key field with the selected
# value if it is already deleted


def set_soft_delete_foreign_key(field, instance, instance_attr, related_class):
    if instance.id and hasattr(instance, instance_attr):
        field.queryset = related_class.objects.all_including_by_pk(getattr(instance, instance_attr).pk)
    else:
        field.queryset = related_class.objects.all()
    return field
