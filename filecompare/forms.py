from django import forms
from .models import FileUpload

class UploadCsvForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ["file"]
    file = forms.FileField(label="Select a CSV File",widget=forms.FileInput(attrs={'accept':'.csv','id':'csv_file'}))

class UploadJsonForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ["file"]

    file = forms.FileField(label="Select a Json File",
                           widget=forms.FileInput(attrs={'accept': '.json', 'id': 'json_file'}))
