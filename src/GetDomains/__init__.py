import azure.functions as func
import json
import logging
from shared.domeneshop import get_domains

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        domains = get_domains()
        
        zones = [
            {
                "id": domain['domain'].replace('.', '_'),
                "name": domain['domain']
            }
            for domain in domains
        ]
        
        logging.info(f"Returning {len(zones)} zones")
        return func.HttpResponse(
            json.dumps(zones),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error listing zones: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )