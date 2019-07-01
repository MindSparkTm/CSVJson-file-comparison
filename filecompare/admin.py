from django.contrib import admin
from .models import PaymentDetail,FileUpload,PaymentMode,File_Validation_Summary

# Register your models here.

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id','file_type', 'progress', 'validation_status')
    readonly_fields = ('date_added',)
    ordering = ['id']
    search_fields = ['id', 'file_type']

class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'payment_source', 'amount','date_last_modified')
    readonly_fields = ('date_added', 'date_last_modified','payment_type','payment_source','amount')
    ordering = ['id']
    search_fields = ['id', 'payment_source']
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'customer_name', 'account_number')
    readonly_fields = ('date_added', 'date_last_modified','payment_mode')
    ordering = ['id']
    search_fields = ['id', 'payment_reference', 'customer_name']

class FileValidationSummaryAdmin(admin.ModelAdmin):
    list_display = ('file', 'date_added')
    readonly_fields = ('date_added', 'date_last_modified')
    ordering = ['id']
    search_fields = ['id', 'file']


admin.site.register(PaymentMode,PaymentModeAdmin)
admin.site.register(PaymentDetail,PaymentDetailAdmin)
admin.site.register(FileUpload,FileUploadAdmin)
admin.site.register(File_Validation_Summary,FileValidationSummaryAdmin)