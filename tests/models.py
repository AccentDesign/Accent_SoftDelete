from django.db import models

from soft_delete.model import SoftDeleteAbstract


class SoftDelete(SoftDeleteAbstract):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ChildSoftDelete(SoftDeleteAbstract):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class ParentSoftDelete(SoftDeleteAbstract):
    name = models.CharField(max_length=20)
    child = models.ForeignKey(ChildSoftDelete, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class ParentCascadeSoftDelete(SoftDeleteAbstract):
    name = models.CharField(max_length=20)
    child = models.ForeignKey(ChildSoftDelete, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
