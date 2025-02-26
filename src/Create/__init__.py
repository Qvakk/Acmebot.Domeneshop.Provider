import azure.functions as func
import json
import logging
from shared.domeneshop import create_txt_record

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        zone_id = req.route_params.get('zoneId')
        record_name = req.route_params.get('recordName')
        logging.info(f"Creating TXT record - Zone: {zone_id}, Record: {record_name}")
        
        try:
            req_body = req.get_json() if req.get_body() else {"type": "TXT", "ttl": 60, "values": []}
        except ValueError:
            req_body = {"type": "TXT", "ttl": 60, "values": []}
            
        success_count = 0
        for value in req_body.get('values', []):
            try:
                create_txt_record(zone_id, record_name, value, req_body.get('ttl', 60))
                success_count += 1
            except Exception as e:
                logging.error(f"Error creating record with value {value}: {str(e)}")
                
        return func.HttpResponse(
            json.dumps({"success": True, "recordsCreated": success_count}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error in Create function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": True}),
            status_code=200,
            mimetype="application/json"
        )