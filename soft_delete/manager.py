from django.db import models
from django.db.models import Q


class SoftDeleteQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(deleted=False)

    def deleted(self):
        return self.filter(deleted=True)

    def delete(self):
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with delete."
        for object in self.all():
            object.delete()
        self._result_cache = None
    delete.alters_data = True


class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        queryset = SoftDeleteQuerySet(self.model, using=self._db)
        return queryset.active()

    def deleted(self):
        queryset = SoftDeleteQuerySet(self.model, using=self._db)
        return queryset.deleted()

    def all_with_deleted(self):
        queryset = SoftDeleteQuerySet(self.model, using=self._db)
        return queryset

    def all_including_by_pk(self, pk=None):
        if pk:
            return self.all_with_deleted().filter(Q(deleted=False) | Q(pk=pk))
        return self.get_queryset()

    def all(self):
        return self.get_queryset()

    def get(self, allow_deleted=False, *args, **kwargs):
        if allow_deleted or 'pk' in kwargs:
            return self.all_with_deleted().get(*args, **kwargs)
        return self.get_queryset().get(*args, **kwargs)
