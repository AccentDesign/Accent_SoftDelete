from django.test import TestCase

from tests.models import Child, ParentFKNothing, ParentFKCascade
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
        ParentFKNothing.objects.create(child=child)
        child.delete()
        self.assertFalse(ParentFKNothing.objects.get(id=child.id).deleted)

    def test_deleting_object_is_still_the_referenced_object_in_a_foreign_key(self):
        child = Child.objects.create(name="child")
        parent = ParentFKNothing.objects.create(child=child)
        child.delete()
        self.assertEqual(ParentFKNothing.objects.get(id=parent.id).child, child)

    def test_deleting_object_will_cascade_when_required(self):
        child = Child.objects.create(name="child")
        ParentFKCascade.objects.create(child=child)
        child.delete()
        self.assertEqual(Child.objects.all().count(), 1)
        self.assertEqual(Child.objects.active().count(), 0)
        self.assertEqual(Child.objects.deleted().count(), 1)
        self.assertEqual(ParentFKCascade.objects.all().count(), 1)
        self.assertEqual(ParentFKCascade.objects.active().count(), 0)
        self.assertEqual(ParentFKCascade.objects.deleted().count(), 1)


class ModelAbstractTests(TestCase):

    def test_deleted_field(self):
        field = SoftDeleteAbstract._meta.get_field('deleted')
        self.assertEqual(field.__class__.__name__, 'BooleanField')
        self.assertFalse(field.editable)
        self.assertFalse(field.default)
        self.assertTrue(field.db_index)

    def test_object_class_is_soft_delete_model_manager(self):
        self.assertEqual(SoftDeleteAbstract._default_manager.__class__, SoftDeleteManager)
