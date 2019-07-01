def validate_empty_cell(row):
    if row['Receipt No.'] and row['Details'] and row['Paid In'] and row['A/C No.']:
        return True
    else:
        return False