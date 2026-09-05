from datetime import datetime


def iso_to_ddmmyyyy(fecha_iso):
    dt = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y")