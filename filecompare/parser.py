import csv,json
from .models import PaymentDetail,FileUpload
from .validators import validate_empty_cell
from django.conf import settings
from .handler import commit_rows,compare_json_rows

class BulkFileParser:

    def __init__(self,file_instance):
        self._file_instance = file_instance
        self.duplicates=[]
        self.invalid_rows=[]
        self.clean_rows=[]

    def get_file_instance(self):
        return self._file_instance

    def get_file_name(self):
        try:
            file_detail = FileUpload.objects.get(id=self._file_instance)
        except FileUpload.DoesNotExist:
            return
        else:
            return file_detail.file.name

    def parse(self):
        raise NotImplementedError

    def add_clean_rows(self,row):
        self.clean_rows.append(row)

    def add_duplicate(self,row):
        self.duplicates.append(row)

    def add_invalid_rows(self,row):
        self.invalid_rows.append(row)

    def get_duplicate(self):
        return self.duplicates

    def get_invalid_rows(self):
        return self.invalid_rows

    def get_clean_rows(self):
        return self.clean_rows

class PaymentCSVParser(BulkFileParser):

    def __init__(self, file_instance,chunk_size):
       super().__init__(file_instance)
       self.chunk_size = chunk_size

    def parse(self):
        self.clean_rows.clear()
        self.duplicates.clear()
        self.invalid_rows.clear()
        file_name = self.get_file_name()
        if file_name is not None:
            with open(settings.MEDIA_URL+file_name, 'r') as csv_file:
                for row in csv.DictReader(csv_file):
                    if validate_empty_cell(row):
                        try:
                            PaymentDetail.objects.get(payment_reference=row['Receipt No.'])
                        except PaymentDetail.DoesNotExist:
                            self.add_clean_rows(row)

                        else:
                            self.add_duplicate(row)
                    else:
                        self.add_invalid_rows(row)

            if len(self.get_clean_rows())>0:
                commit_task=commit_rows.delay('payment',self.get_clean_rows(),self.chunk_size)
                return commit_task
            else:
                return

class PaymentJsonParser(BulkFileParser):

    def __init__(self, file_instance):
       super().__init__(file_instance)
       self.current_row=[]
       self.json_row =[]
       self.row_csv=[]
       self.row_json=[]

    def set_json_row(self,row):
        self.row_json.append(row)
    def set_csv_row(self,row):
        self.row_csv.append(row)
    def get_json_row(self):
        return self.row_json
    def get_csv_row(self):
        return self.row_csv
    def get_invalid_rows(self):
        return self.invalid_rows
    def _check_diff(self,database_row,json_row):
        if database_row!=json_row:
            return False
        else:
            return True


    def parse(self):
        self.row_json.clear()
        self.row_csv.clear()
        self.invalid_rows.clear()
        file_name = self.get_file_name()
        if file_name is not None:
            with open(settings.MEDIA_URL+file_name, 'r') as json_file:
                json_rows = json.load(json_file)
                task_compare=compare_json_rows.apply_async((self,"payment",json_rows),serializer='pickle')
            return True,task_compare
        else:
            return False

