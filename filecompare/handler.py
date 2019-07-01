from celery import shared_task, current_task
from .bulk_create_helper import BulkCreateManager
from .models import PaymentDetail,PaymentMode,FileUpload,File_Validation_Summary

@shared_task
def commit_rows(file_type,rows,chunk_size):
    bulk_mgr = BulkCreateManager(chunk_size=chunk_size)
    if file_type =='payment':
        total_rows = len(rows)
        i = 1
        for row in rows:
            payment_detail = row['Details'].split()
            customer_name = ''.join(payment_detail[4:])
            if payment_detail[0].lower()=='credit':
                payment_mode = PaymentMode(payment_type=1,payment_source=payment_detail[2],
                                           amount=row['Paid In'])
                payment_mode.save()
            elif payment_detail[0].lower()=='mpesa':
                payment_mode = PaymentMode(payment_type=0,payment_source=payment_detail[2],amount=row['Paid In'])
                payment_mode.save()

            bulk_mgr.add(PaymentDetail(payment_reference=row['Receipt No.'],
                                       customer_name=customer_name,payment_mode=payment_mode,
                                        account_number=row['A/C No.']))
            bulk_mgr.done()
            percent = int(100 * float(i) / float(total_rows))
            i = i+1
            current_task.update_state(state='PROGRESS',
                                      meta={'process_percent':percent})
        return True

@shared_task
def compare_json_rows(obj,file_type,rows):
    if file_type=='payment':
        total_rows = len(rows)
        i = 1
        for row in rows:
            # ref,name,amount,acc,src
            obj.current_row.clear()
            obj.json_row.clear()
            try:
                _payment = PaymentDetail.objects.get(payment_reference=row['ref'])
            except PaymentDetail.DoesNotExist:
                obj.add_invalid_rows(row)
            else:
                obj.current_row.append(_payment.payment_reference)
                obj.current_row.append(_payment.customer_name)
                obj.current_row.append(_payment.payment_mode.amount)
                obj.current_row.append(_payment.account_number)
                if _payment.payment_mode.payment_type == 0:
                    obj.current_row.append('mpesa')
                elif _payment.payment_mode.payment_type == 1:
                    obj.current_row.append('creditcard')
                obj.current_row.append(_payment.payment_mode.payment_source)
                obj.json_row.append(row['ref'])
                name = row['name'].replace(' ', '')
                obj.json_row.append(name)
                obj.json_row.append(row['amount'])
                obj.json_row.append(row['acc'])
                payment_source_detail = row['src'].split(':')
                obj.json_row.append(payment_source_detail[0])
                obj.json_row.append(payment_source_detail[1])
                if obj.json_row == obj.current_row:
                    pass
                else:
                    obj.set_json_row(row)
                    csv_row = [_payment.payment_reference, name, _payment.payment_mode.amount, _payment.account_number,
                               payment_source_detail[0], payment_source_detail[1]]
                    obj.set_csv_row(csv_row)
        percent = int(100 * float(i) / float(total_rows))
        i = i + 1
        current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': percent})
        json_file = FileUpload.objects.get(id=obj.get_file_instance())
        json_file.append_validation_summary(obj.get_invalid_rows(),obj.get_csv_row(),obj.get_json_row())
        json_file.set_progress(percent)
        file_validation_summary = File_Validation_Summary(file=json_file)
        file_validation_summary.save_validation_summary(obj.get_invalid_rows(),obj.get_csv_row(),obj.get_json_row())
    return True
