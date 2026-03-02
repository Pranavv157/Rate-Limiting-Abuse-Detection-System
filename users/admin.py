from django.contrib import admin

# Register your models here.


@admin.register(...)
class AbuseAdmin(admin.ModelAdmin):
    list_display = ("identity", "score", "last_seen")