import itertools

from django.contrib.admin.utils import NestedObjects
from django.db import router


def related_objects(obj):
    collector = NestedObjects(using=router.db_for_write(obj))
    collector.collect([obj])

    def flatten(elem):
        if isinstance(elem, list):
            return itertools.chain.from_iterable(map(flatten, elem))
        elif obj != elem:
            return (elem,)
        return ()
    return flatten(collector.nested())
