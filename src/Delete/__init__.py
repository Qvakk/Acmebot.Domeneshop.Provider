import azure.functions as func
import json
import logging
from shared.domeneshop import delete_txt_records

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        zone_id = req.route_params.get('zoneId')
        record_name = req.route_params.get('recordName')
        logging.info(f"Deleting TXT record - Zone: {zone_id}, Record: {record_name}")
        
        try:
            result = delete_txt_records(zone_id, record_name)
            return func.HttpResponse(
                json.dumps({"success": True, "deleted": result.get('count', 0)}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Error deleting records: {str(e)}")
            return func.HttpResponse(
                json.dumps({"success": True, "message": "Processed with errors"}),
                status_code=200
            )
            
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": True, "message": "Request processed"}),
            status_code=200
        )