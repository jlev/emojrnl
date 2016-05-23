from django.contrib import admin
from journal.models import Journal, Entry


class JournalAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('hashid', 'num_entries', 'last_updated')
    list_filter = ('confirmed',)
    readonly_fields = ('hashid', 'last_updated')


class EntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('hashid', 'txt', 'created_at')
    #readonly_fields = ('txt', 'created_at')


admin.site.register(Journal, JournalAdmin)
admin.site.register(Entry, EntryAdmin)
