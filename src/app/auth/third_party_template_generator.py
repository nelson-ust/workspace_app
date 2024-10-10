import pandas as pd
from fastapi import HTTPException
from io import BytesIO

def generate_template(file_type: str):
    columns = ["name", "email", "phone_number", "site_id"]
    data = pd.DataFrame(columns=columns)

    if file_type == "csv":
        output = BytesIO()
        data.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue(), "text/csv"
    elif file_type == "excel":
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        data.to_excel(writer, index=False, sheet_name='ThirdPartyParticipants')
        writer.save()
        output.seek(0)
        return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Supported types are 'csv' and 'excel'.")
