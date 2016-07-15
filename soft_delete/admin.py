class ActiveAdminMixin(object):
    def get_queryset(self, request):
        queryset = super(ActiveAdminMixin, self).get_queryset(request)
        return queryset.filter(deleted=False)
