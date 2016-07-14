from django.db import models
from django.test import TestCase

from tests.models import Child, Group, Membership, Parent
from soft_delete.manager import SoftDeleteManager
from soft_delete.model import SoftDeleteAbstract


class ModelManagerTests(TestCase):

    ##################################
    # querysets                      #
    ##################################

    def test_querysets_with_no_deleted_objects(self):
        Child.objects.create(name='bill')
        Child.objects.create(name='ted')
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 2)
        self.assertEqual(Child.objects.deleted().count(), 0)

    def test_querysets_with_deleted_objects(self):
        Child.objects.create(name='bill', deleted=True)
        Child.objects.create(name='ted', deleted=True)
        Child.objects.create(name='mike')
        self.assertEqual(Child.objects.all().count(), 3)
        self.assertEqual(Child.objects.active().count(), 1)
        self.assertEqual(Child.objects.deleted().count(), 2)

    ##################################
    # get method                     #
    ##################################

    def test_get_contains_objects(self):
        obj = Child.objects.create(name='bill')
        Child.objects.get(id=obj.id)

    def test_get_contains_deleted_objects(self):
        obj = Child.objects.create(name='bill', deleted=True)
        Child.objects.get(id=obj.id)

    ##################################
    # active_including_by_PK         #
    ##################################

    def test_active_including_by_PK__includes_deleted(self):
        Child.objects.create(name='bill', deleted=True)
        ted = Child.objects.create(name='ted', deleted=True)
        Child.objects.create(name='mike')
        self.assertEqual(Child.objects.active_including_by_PK(ted.id).count(), 2)

    def test_active_including_by_PK__passed_pk_does_not_need_to_be_a_deleted_object(self):
        Child.objects.create(name='bill', deleted=True)
        ted = Child.objects.create(name='ted')
        Child.objects.create(name='mike')
        self.assertEqual(Child.objects.active_including_by_PK(ted.pk).count(), 2)

    def test_active_including_by_PK__can_be_passed_none_pk(self):
        Child.objects.create(name='bill', deleted=True)
        Child.objects.create(name='ted', deleted=True)
        Child.objects.create(name='mike')
        self.assertEqual(Child.objects.active_including_by_PK().count(), 1)

    ##################################
    # deleting tests                 #
    ##################################

    def test_can_delete_a_single_object(self):
        obj = Child.objects.create(name='bill')
        obj.delete()
        self.assertEqual(Child.objects.all().count(), 1)
        self.assertEqual(Child.objects.active().count(), 0)
        self.assertEqual(Child.objects.deleted().count(), 1)

    def test_can_undelete_a_single_object(self):
        obj = Child.objects.create(name='bill', deleted=True)
        obj.undelete()
        self.assertEqual(Child.objects.all().count(), 1)
        self.assertEqual(Child.objects.active().count(), 1)
        self.assertEqual(Child.objects.deleted().count(), 0)

    def test_can_delete_a_queryset(self):
        Child.objects.create(name='bill')
        Child.objects.create(name='ben')
        Child.objects.all().delete()
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 0)
        self.assertEqual(Child.objects.deleted().count(), 2)

    def test_can_undelete_a_queryset(self):
        Child.objects.create(name='bill', deleted=True)
        Child.objects.create(name='bob', deleted=True)
        Child.objects.deleted().undelete()
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 2)
        self.assertEqual(Child.objects.deleted().count(), 0)

    def test_can_delete_a_filter(self):
        Child.objects.create(name='bill')
        Child.objects.create(name='ben')
        Child.objects.filter(name='bill').delete()
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 1)
        self.assertEqual(Child.objects.deleted().count(), 1)

    def test_can_undelete_a_filter(self):
        Child.objects.create(name='bill', deleted=True)
        Child.objects.create(name='bob')
        Child.objects.filter(name='bill').undelete()
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 2)
        self.assertEqual(Child.objects.deleted().count(), 0)


class CascadeForeignKeyTests(TestCase):

    def test_deleting_object_does_not_cascade(self):
        child = Child.objects.create(name="child")
        Parent.objects.create(child=child)
        child.delete()
        self.assertFalse(Parent.objects.get(id=child.id).deleted)

    def test_deleting_object_is_still_the_referenced_object_in_a_foreign_key(self):
        child = Child.objects.create(name="child")
        parent = Parent.objects.create(child=child)
        child.delete()
        self.assertEqual(Parent.objects.get(id=parent.id).child, child)

    def test_deleting_object_will_cascade_when_required(self):
        Parent._meta.get_field('child').rel.on_delete = models.CASCADE
        child = Child.objects.create(name="child")
        Parent.objects.create(child=child)
        child.delete()
        self.assertEqual(Child.objects.all().count(), 1)
        self.assertEqual(Child.objects.active().count(), 0)
        self.assertEqual(Child.objects.deleted().count(), 1)
        self.assertEqual(Parent.objects.all().count(), 1)
        self.assertEqual(Parent.objects.active().count(), 0)
        self.assertEqual(Parent.objects.deleted().count(), 1)


class CascadeManyToManyThroughTests(TestCase):

    def test_deleting_object_is_still_in_the_joining_relationship(self):
        child1 = Child.objects.create(name="child 1")
        child2 = Child.objects.create(name="child 2")
        group = Group.objects.create(name="group")
        Membership.objects.create(group=group, child=child1)
        Membership.objects.create(group=group, child=child2)
        child1.delete()
        self.assertEqual(Group.objects.all().count(), 1)
        self.assertEqual(Group.objects.active().count(), 1)
        self.assertEqual(Group.objects.deleted().count(), 0)
        self.assertEqual(Membership.objects.all().count(), 2)
        self.assertEqual(Membership.objects.active().count(), 2)
        self.assertEqual(Membership.objects.deleted().count(), 0)
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 1)
        self.assertEqual(Child.objects.deleted().count(), 1)

    def test_deleting_object_will_cascade_when_required(self):
        Membership._meta.get_field('child').rel.on_delete = models.CASCADE
        child1 = Child.objects.create(name="child 1")
        child2 = Child.objects.create(name="child 2")
        group = Group.objects.create(name="group")
        Membership.objects.create(group=group, child=child1)
        Membership.objects.create(group=group, child=child2)
        child1.delete()
        self.assertEqual(Group.objects.all().count(), 1)
        self.assertEqual(Group.objects.active().count(), 1)
        self.assertEqual(Group.objects.deleted().count(), 0)
        self.assertEqual(Membership.objects.all().count(), 2)
        self.assertEqual(Membership.objects.active().count(), 1)
        self.assertEqual(Membership.objects.deleted().count(), 1)
        self.assertEqual(Child.objects.all().count(), 2)
        self.assertEqual(Child.objects.active().count(), 1)
        self.assertEqual(Child.objects.deleted().count(), 1)


class ModelAbstractTests(TestCase):

    def test_deleted_field(self):
        field = SoftDeleteAbstract._meta.get_field('deleted')
        self.assertEqual(field.__class__.__name__, 'BooleanField')
        self.assertFalse(field.editable)
        self.assertFalse(field.default)
        self.assertTrue(field.db_index)

    def test_object_class_is_soft_delete_model_manager(self):
        self.assertEqual(SoftDeleteAbstract._default_manager.__class__, SoftDeleteManager)
