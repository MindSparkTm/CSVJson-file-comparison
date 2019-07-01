from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class FileUpload(models.Model):
    STATUS_NEW = 'NEW'
    STATUS_VALIDATION_PENDING = 'VP'
    STATUS_VALIDATING = 'VIP'
    STATUS_VALIDATED = 'VC'
    STATUS_CHOICES = (
        (STATUS_NEW, 'New Upload'),
        (STATUS_VALIDATION_PENDING, 'Validation Pending'),
        (STATUS_VALIDATING, 'Validating'),
        (STATUS_VALIDATED, 'Validated'),
    )
    FILE_INCOMING_PAYMENT_SUMMARY = 'IPS'
    FILE_OTHER= 'Other'
    FILE_TYPE=(
        (FILE_INCOMING_PAYMENT_SUMMARY,'Incoming Payment Summary'),
        (FILE_OTHER,'File type not recognized'),
      )
    file = models.FileField(blank=True)
    file_type = models.CharField(max_length=40,choices=FILE_TYPE,default=FILE_OTHER)
    progress = models.IntegerField(default=0)
    validation_status = models.CharField(choices=STATUS_CHOICES,max_length=15,blank=True,null=True)
    validation_results = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'File Upload Details:{} {}'.format(self.id, self.file_type)

    def append_validation_summary(self,invalid_row,json_row,csv_row):
        self.validation_results = "{}{}{}".format(invalid_row,json_row,csv_row)
        self.save()

    def set_progress(self,value):
        self.progress = value
        self.save()


    class Meta:
        verbose_name = _('FileUpload')
        verbose_name_plural = _('FileUpload Details')
        ordering = ['date_added']

class File_Validation_Summary(models.Model):

    file = models.ForeignKey(FileUpload, on_delete=models.PROTECT, blank=True, null=True)
    csv_diff_rows = models.TextField(blank=True,null=True)
    json_diff_rows=models.TextField(blank=True,null=True)
    invalid_rows = models.TextField(blank=True,null=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save_validation_summary(self,invalid_row,json_row,csv_row):
        self.csv_diff_rows = csv_row
        self.json_diff_rows = json_row
        self.invalid_rows = invalid_row
        self.save()

    def __str__(self):
        return u'FileValidationSummary Details:{} {}'.format(self.id, self.file)

    class Meta:
        verbose_name = _('FileValidation Summary')
        verbose_name_plural = _('FileValidation Summary Details')
        ordering = ['date_added']


class PaymentMode(models.Model):
    _type=(
        (0,'mpesa'),
        (1,'creditcard'),
    )

    payment_type = models.IntegerField(choices=_type,null=True,blank=True)
    payment_source = models.CharField(max_length=20,null=True,blank=True)
    amount = models.FloatField()
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'PaymentMode Details:{} {}'.format(self.id, self.payment_source)

    class Meta:
        verbose_name = _('PaymentMode')
        verbose_name_plural = _('Payment Mode Details')
        ordering = ['date_added']


class PaymentDetail(models.Model):
    payment_reference = models.CharField(max_length=20,unique=True)
    customer_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20)
    payment_mode = models.OneToOneField(PaymentMode,on_delete=models.CASCADE,null=True,blank=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'Account Details:{} {}'.format(self.payment_reference,self.customer_name)

    class Meta:
        verbose_name = _('Payment Detail')
        verbose_name_plural = _('Payment Details')
        ordering = ['customer_name']
