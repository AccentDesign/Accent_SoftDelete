from django import forms
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from soft_delete.admin import ActiveAdmin
from soft_delete.helpers import set_soft_delete_foreign_key
from .models import ParentSoftDelete, ChildSoftDelete


class MockRequest(object):
    pass


request = MockRequest()


class MyForm(forms.ModelForm):
    class Meta:
        model = ParentSoftDelete
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        set_soft_delete_foreign_key(self.fields['child'], self.instance, 'child', ChildSoftDelete)


class ModelAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()

    def test_queryset_only_contains_active(self):
        object = ChildSoftDelete.objects.create(name='foo')
        ChildSoftDelete.objects.create(name='bar', deleted=True)

        class MyAdmin(ActiveAdmin):
            pass

        ma = MyAdmin(ChildSoftDelete, self.site)
        self.assertEqual(ma.get_queryset(request).count(), 1)
        ma.get_queryset(request).get(id=object.id)

    def test_active_only_in_options_when_none_selected(self):
        child1 = ChildSoftDelete.objects.create(name='child 1')
        ChildSoftDelete.objects.create(name='child 2', deleted=True)
        parent = ParentSoftDelete()

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(ParentSoftDelete, self.site)
        form = ma.get_form(request)(instance=parent)

        self.assertHTMLEqual(
            str(form["child"]),
            '<div class="related-widget-wrapper">'
            '<select name="child" id="id_child">'
            '<option value="" selected="selected">---------</option>'
            '<option value="%d">child 1</option>'
            '</select></div>' % child1.id
        )

    def test_active_only_in_options_when_active_selected(self):
        child1 = ChildSoftDelete.objects.create(name='child 1')
        ChildSoftDelete.objects.create(name='child 2', deleted=True)
        parent = ParentSoftDelete.objects.create(name='parent', child=child1)

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(ParentSoftDelete, self.site)
        form = ma.get_form(request)(instance=parent)

        self.assertHTMLEqual(
            str(form["child"]),
            '<div class="related-widget-wrapper">'
            '<select name="child" id="id_child">'
            '<option value="">---------</option>'
            '<option value="%d" selected="selected">child 1</option>'
            '</select></div>' % child1.id
        )

    def test_deleted_in_options_deleted_selected(self):
        child1 = ChildSoftDelete.objects.create(name='child 1')
        child2 = ChildSoftDelete.objects.create(name='child 2', deleted=True)
        parent = ParentSoftDelete.objects.create(name='parent', child=child2)

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(ParentSoftDelete, self.site)
        form = ma.get_form(request)(instance=parent)

        self.assertHTMLEqual(
            str(form["child"]),
            '<div class="related-widget-wrapper">'
            '<select name="child" id="id_child">'
            '<option value="">---------</option>'
            '<option value="%d">child 1</option>'
            '<option value="%d" selected="selected">child 2</option>'
            '</select></div>' % (child1.id, child2.id)
        )
