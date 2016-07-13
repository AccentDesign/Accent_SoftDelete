from django.db import models
from django.db.models import Q


class SoftDeleteQuerySet(models.query.QuerySet):
    def delete(self):
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with delete."
        for object in self.all():
            object.delete()
        self._result_cache = None
    delete.alters_data = True

    def undelete(self):
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with delete."
        for object in self.all():
            object.undelete()
        self._result_cache = None
    undelete.alters_data = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted(self):
        return self.get_queryset().filter(deleted=True)

    def active(self):
        return self.get_queryset().filter(deleted=False)

    def active_including_by_PK(self, pk=None):
        if pk:
            return self.get_queryset().filter(Q(deleted=False) | Q(pk=pk))
        return self.active()

    def all(self):
        return self.get_queryset()
