from django.contrib import admin


class ActiveAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(ActiveAdmin, self).get_queryset(request)
        return queryset.filter(deleted=False)
