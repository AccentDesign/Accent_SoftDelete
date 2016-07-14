from django.db import models

from soft_delete.model import SoftDeleteAbstract


class Child(SoftDeleteAbstract):
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ParentFKNothing(SoftDeleteAbstract):
    child = models.ForeignKey(Child, on_delete=models.DO_NOTHING)


class ParentFKCascade(SoftDeleteAbstract):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
