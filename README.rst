*****************
Accent_SoftDelete
*****************

|Build_Status| |Coverage_Status|

.. |Build_Status| image:: https://circleci.com/gh/AccentDesign/Accent_SoftDelete.svg?style=svg
   :target: https://circleci.com/gh/AccentDesign/Accent_SoftDelete
.. |Coverage_Status| image:: http://img.shields.io/coveralls/AccentDesign/Accent_SoftDelete/master.svg
   :target: https://coveralls.io/r/AccentDesign/Accent_SoftDelete?branch=master

Description
***********

Soft delete plugin for django


Getting Started
***************

Installation::

   pip install git+https://github.com/AccentDesign/Accent_SoftDelete.git@master#egg=soft_delete

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


Model form, will allow a selected fk that has been deleted available until saved (example of above models)::

   from soft_delete.admin import ActiveAdmin
   from soft_delete.helpers import set_soft_delete_foreign_key

   class MyForm(forms.ModelForm):
       class Meta:
           model = Parent2
           fields = '__all__'

       def __init__(self, *args, **kwargs):
           super(MyForm, self).__init__(*args, **kwargs)
           set_soft_delete_foreign_key(self.fields['child'], self.instance, 'child', Child)
