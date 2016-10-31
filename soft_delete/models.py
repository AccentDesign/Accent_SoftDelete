from django.db import models

from .manager import SoftDeleteManager
from .utils import related_objects


class SoftDeleteAbstract(models.Model):
    deleted = models.BooleanField(default=False, editable=False, db_index=True)

    class Meta:
        abstract = True

    objects = SoftDeleteManager()

    def delete(self, **kwargs):
        self.deleted = True
        for object in related_objects(self):
            object.delete()
        super(SoftDeleteAbstract, self).save(**kwargs)
