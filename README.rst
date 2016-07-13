*****************
Accent_SoftDelete
*****************

|Build_Status|

.. |Build_Status| image:: https://circleci.com/gh/AccentDesign/Accent_SoftDelete.svg?style=svg&circle-token=d9427f13f6a15f62a81775f1d4cc2e656858b7f3
   :target: https://circleci.com/gh/AccentDesign/Accent_SoftDelete

Description
***********

Soft delete plugin for django


Getting Started
***************

Installation::

   pip install -e git://github.com/AccentDesign/Accent_SoftDelete.git#egg=soft_delete

settings.py::

   INSTALLED_APPS = [
       ...
       'soft_delete',
       ...
   ]


Usage
*****

Model defs::

   from soft_delete.models import SoftDeleteAbstract


   class Child(SoftDeleteAbstract):
       name = models.CharField(max_length=20)


   class Parent1(SoftDeleteAbstract):
       name = models.CharField(max_length=20)
       child = models.ForeignKey(Child, on_delete=models.CASCADE)


   class Parent2(SoftDeleteAbstract):
       name = models.CharField(max_length=20)
       child = models.ForeignKey(Child, on_delete=models.DO_NOTHING)


Admin site (example of above models)::

   from soft_delete.admin import ActiveAdmin
   from soft_delete.helpers import set_soft_delete_foreign_key

   class MyForm(forms.ModelForm):
       class Meta:
           model = Parent2
           fields = '__all__'

       def __init__(self, *args, **kwargs):
           super(MyForm, self).__init__(*args, **kwargs)
           set_soft_delete_foreign_key(self.fields['child'], self.instance, 'child', Child)
