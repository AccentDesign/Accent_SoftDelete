from django.db import models

from soft_delete.models import SoftDeleteAbstract


class Child(SoftDeleteAbstract):
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Parent(SoftDeleteAbstract):
    child = models.ForeignKey(Child, on_delete=models.DO_NOTHING)


class Group(SoftDeleteAbstract):
    name = models.CharField(max_length=20)
    members = models.ManyToManyField(Child, through='Membership')


class Membership(SoftDeleteAbstract):
    child = models.ForeignKey(Child, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)


class UniqueModel(SoftDeleteAbstract):
    name = models.CharField(max_length=20, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)

    class Meta:
        unique_together = ('age', 'gender')
