from django import forms
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from soft_delete.admin import ActiveAdmin
from soft_delete.helpers import set_soft_delete_foreign_key
from .models import Child, Parent


class MockRequest(object):
    pass


request = MockRequest()


class MyForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        set_soft_delete_foreign_key(self.fields['child'], self.instance, 'child', Child)


class ModelAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()

    def test_queryset_only_contains_active(self):
        object = Child.objects.create(name='foo')
        Child.objects.create(name='bar', deleted=True)

        class MyAdmin(ActiveAdmin):
            pass

        ma = MyAdmin(Child, self.site)
        self.assertEqual(ma.get_queryset(request).count(), 1)
        ma.get_queryset(request).get(id=object.id)

    def test_active_only_in_options_when_none_selected(self):
        child1 = Child.objects.create(name='child 1')
        Child.objects.create(name='child 2', deleted=True)
        parent = Parent()

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(Parent, self.site)
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
        child1 = Child.objects.create(name='child 1')
        Child.objects.create(name='child 2', deleted=True)
        parent = Parent.objects.create(child=child1)

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(Parent, self.site)
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
        child1 = Child.objects.create(name='child 1')
        child2 = Child.objects.create(name='child 2', deleted=True)
        parent = Parent.objects.create(child=child2)

        class MyAdmin(ActiveAdmin):
            form = MyForm

        ma = MyAdmin(Parent, self.site)
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
