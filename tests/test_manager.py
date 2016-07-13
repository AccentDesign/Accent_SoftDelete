from django.test import TestCase

from tests.models import SoftDelete, ParentSoftDelete, ParentCascadeSoftDelete, ChildSoftDelete
from soft_delete.manager import SoftDeleteManager
from soft_delete.model import SoftDeleteAbstract


class ModelManagerTests(TestCase):

    ##################################
    # querysets                      #
    ##################################

    def test_querysets_with_no_deleted_objects(self):
        SoftDelete.objects.create(name='bill')
        SoftDelete.objects.create(name='ted')
        self.assertEqual(SoftDelete.objects.all().count(), 2)
        self.assertEqual(SoftDelete.objects.active().count(), 2)
        self.assertEqual(SoftDelete.objects.deleted().count(), 0)

    def test_querysets_with_deleted_objects(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        SoftDelete.objects.create(name='ted', deleted=True)
        SoftDelete.objects.create(name='mike')
        self.assertEqual(SoftDelete.objects.all().count(), 3)
        self.assertEqual(SoftDelete.objects.active().count(), 1)
        self.assertEqual(SoftDelete.objects.deleted().count(), 2)

    ##################################
    # get method                     #
    ##################################

    def test_get_contains_objects(self):
        obj = SoftDelete.objects.create(name='bill')
        SoftDelete.objects.get(id=obj.id)

    def test_get_contains_deleted_objects(self):
        obj = SoftDelete.objects.create(name='bill', deleted=True)
        SoftDelete.objects.get(id=obj.id)

    ##################################
    # active_including_by_PK         #
    ##################################

    def test_active_including_by_PK__includes_deleted(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        ted = SoftDelete.objects.create(name='ted', deleted=True)
        SoftDelete.objects.create(name='mike')
        self.assertEqual(SoftDelete.objects.active_including_by_PK(ted.id).count(), 2)

    def test_active_including_by_PK__passed_pk_does_not_need_to_be_a_deleted_object(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        ted = SoftDelete.objects.create(name='ted')
        SoftDelete.objects.create(name='mike')
        self.assertEqual(SoftDelete.objects.active_including_by_PK(ted.pk).count(), 2)

    def test_active_including_by_PK__can_be_passed_none_pk(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        SoftDelete.objects.create(name='ted', deleted=True)
        SoftDelete.objects.create(name='mike')
        self.assertEqual(SoftDelete.objects.active_including_by_PK().count(), 1)

    ##################################
    # deleting tests                 #
    ##################################

    def test_can_delete_a_single_object(self):
        obj = SoftDelete.objects.create(name='bill')
        obj.delete()
        self.assertEqual(SoftDelete.objects.all().count(), 1)
        self.assertEqual(SoftDelete.objects.active().count(), 0)
        self.assertEqual(SoftDelete.objects.deleted().count(), 1)

    def test_can_undelete_a_single_object(self):
        obj = SoftDelete.objects.create(name='bill', deleted=True)
        obj.undelete()
        self.assertEqual(SoftDelete.objects.all().count(), 1)
        self.assertEqual(SoftDelete.objects.active().count(), 1)
        self.assertEqual(SoftDelete.objects.deleted().count(), 0)

    def test_can_delete_a_queryset(self):
        SoftDelete.objects.create(name='bill')
        SoftDelete.objects.create(name='ben')
        SoftDelete.objects.all().delete()
        self.assertEqual(SoftDelete.objects.all().count(), 2)
        self.assertEqual(SoftDelete.objects.active().count(), 0)
        self.assertEqual(SoftDelete.objects.deleted().count(), 2)

    def test_can_undelete_a_queryset(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        SoftDelete.objects.create(name='bob', deleted=True)
        SoftDelete.objects.deleted().undelete()
        self.assertEqual(SoftDelete.objects.all().count(), 2)
        self.assertEqual(SoftDelete.objects.active().count(), 2)
        self.assertEqual(SoftDelete.objects.deleted().count(), 0)

    def test_can_delete_a_filter(self):
        SoftDelete.objects.create(name='bill')
        SoftDelete.objects.create(name='ben')
        SoftDelete.objects.filter(name='bill').delete()
        self.assertEqual(SoftDelete.objects.all().count(), 2)
        self.assertEqual(SoftDelete.objects.active().count(), 1)
        self.assertEqual(SoftDelete.objects.deleted().count(), 1)

    def test_can_undelete_a_filter(self):
        SoftDelete.objects.create(name='bill', deleted=True)
        SoftDelete.objects.create(name='bob')
        SoftDelete.objects.filter(name='bill').undelete()
        self.assertEqual(SoftDelete.objects.all().count(), 2)
        self.assertEqual(SoftDelete.objects.active().count(), 2)
        self.assertEqual(SoftDelete.objects.deleted().count(), 0)

    ##################################
    # cascading delete tests         #
    ##################################

    def test_deleting_object_does_not_cascade(self):
        child = ChildSoftDelete.objects.create(name="child")
        ParentSoftDelete.objects.create(name="parent", child=child)
        child.delete()
        self.assertFalse(ParentSoftDelete.objects.get(id=child.id).deleted)

    def test_deleting_object_is_still_the_referenced_object_in_a_foreign_key(self):
        child = ChildSoftDelete.objects.create(name="child")
        parent = ParentSoftDelete.objects.create(name="parent", child=child)
        child.delete()
        self.assertEqual(ParentSoftDelete.objects.get(id=parent.id).child, child)

    def test_deleting_object_will_cascade_when_required(self):
        child = ChildSoftDelete.objects.create(name="child")
        ParentCascadeSoftDelete.objects.create(name="parent", child=child)
        child.delete()
        self.assertEqual(ChildSoftDelete.objects.all().count(), 1)
        self.assertEqual(ChildSoftDelete.objects.active().count(), 0)
        self.assertEqual(ChildSoftDelete.objects.deleted().count(), 1)
        self.assertEqual(ParentCascadeSoftDelete.objects.all().count(), 1)
        self.assertEqual(ParentCascadeSoftDelete.objects.active().count(), 0)
        self.assertEqual(ParentCascadeSoftDelete.objects.deleted().count(), 1)


class ModelAbstractTests(TestCase):

    def test_deleted_field(self):
        field = SoftDeleteAbstract._meta.get_field('deleted')
        self.assertEqual(field.__class__.__name__, 'BooleanField')
        self.assertFalse(field.editable)
        self.assertFalse(field.default)
        self.assertTrue(field.db_index)

    def test_object_class_is_soft_delete_model_manager(self):
        self.assertEqual(SoftDeleteAbstract._default_manager.__class__, SoftDeleteManager)
