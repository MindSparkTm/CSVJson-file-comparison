# Create your views here.
from django.views.generic import View,CreateView
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadCsvForm,UploadJsonForm
from celery.result import AsyncResult
import json
from .parser import PaymentCSVParser,PaymentJsonParser
from .models import File_Validation_Summary

class PaymentCsvSummary(CreateView):
    def get(self,request):
        csv_form = UploadCsvForm
        json_form = UploadJsonForm
        return render(request, 'filecompare/upload.html', {'csv_form': csv_form, 'json_form': json_form})

    def post(self, request):
        csv_form = UploadCsvForm(request.POST,request.FILES)
        if csv_form.is_valid() and request.is_ajax():
            csv_instance=csv_form.save()
            payment_csv_parser = PaymentCSVParser(csv_instance.id,20)
            payment_parser_result = payment_csv_parser.parse()
            if payment_parser_result is not None:
                data ={
                    "result":"success",
                    "task_id":payment_parser_result.id,
                    "duplicates":payment_csv_parser.get_duplicate(),
                    "invalid_rows":payment_csv_parser.get_invalid_rows()
                }
                json_data = json.dumps(data)

                return HttpResponse (json_data,content_type="application/json")
            else:
                data = {
                    "result": "fail",
                    "duplicates": payment_csv_parser.get_duplicate(),
                    "invalid_rows": payment_csv_parser.get_invalid_rows()
                }
                return HttpResponse(json.dumps(data),content_type="application/json")
        else:
            return HttpResponse ('Failed')

class PaymentJsonSummary(View):

    def post(self,request):
        json_form = UploadJsonForm(request.POST,request.FILES)
        if json_form.is_valid() and request.is_ajax():
            json_instance = json_form.save()
            payment_json_parser = PaymentJsonParser(json_instance.id)
            payment_parser_result,_task_id = payment_json_parser.parse()
            if payment_parser_result:
                result={
                    'status':'success',
                    'task_id':_task_id.id,
                    'instance_id':json_instance.id
                }
                result = json.dumps(result)
                return HttpResponse(result,content_type='application/json')
            else:
                result={
                    'status':'failure'
                }
                result = json.dumps(result)

                return HttpResponse(result,content_type='application/json')
        else:
            return HttpResponse('Failed')

def get_validation_result(request,instance_id,file_type):
    if request.method=='GET':
        if file_type=='payment':
            try:
                validation_summary = File_Validation_Summary.objects.get(file__id=instance_id)
            except File_Validation_Summary.DoesNotExist:
                return HttpResponse('No file found for that file id')
            else:
                data = {
                    "csv_rows": validation_summary.csv_diff_rows,
                    "json_rows": validation_summary.json_diff_rows,
                    "invalid_rows": validation_summary.invalid_rows}
                data = json.dumps(data)
                return HttpResponse(data, content_type='application/json')
        else:
            return HttpResponse('Invalid file Type')

def task_state(request):
    data = 'Fail'
    if request.is_ajax():
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        if body_data['task_id'] is not None:
            task = AsyncResult(body_data['task_id'])
            data = {
                'state': task.state,
                'result': task.result,
            }

        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')
