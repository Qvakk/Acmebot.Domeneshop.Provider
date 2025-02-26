import os
import json
import logging
import traceback
from domeneshop import Client

def get_client():
    token = os.environ.get('DOMENESHOP_TOKEN')
    secret = os.environ.get('DOMENESHOP_SECRET')
    
    if not token or not secret:
        raise ValueError("Missing DOMENESHOP_TOKEN or DOMENESHOP_SECRET environment variables")
    
    return Client(token, secret)

def get_domains():
    try:
        client = get_client()
        domains = client.get_domains()
        logging.info(f"Retrieved {len(domains)} domains")
        return domains
    except Exception as e:
        logging.error(f"Error retrieving domains: {str(e)}")
        raise

def get_domain_id(zone_id):
    if isinstance(zone_id, int) or zone_id.isdigit():
        return int(zone_id)
        
    domain_name = zone_id.replace('_', '.')
    domains = get_domains()
    domain = next((d for d in domains if d['domain'] == domain_name), None)
    
    if not domain:
        raise ValueError(f"Domain not found: {domain_name}")
        
    return domain['id']

def extract_subdomain(host, domain_name):
    if host == domain_name or host == f"{domain_name}.":
        return "@"
    elif host.endswith(f".{domain_name}"):
        return host[:-len(domain_name)-1].rstrip('.')
    return host

def create_txt_record(domain_id, host, value, ttl=60):
    try:
        client = get_client()
        numeric_id = get_domain_id(domain_id)
        
        domain_info = next((d for d in get_domains() if d['id'] == numeric_id), None)
        if not domain_info:
            raise ValueError(f"Domain with ID {numeric_id} not found")
            
        subdomain = extract_subdomain(host, domain_info['domain'])
        if subdomain == "_acme-challenge.":
            subdomain = "_acme-challenge"
            
        record_data = {
            "host": subdomain,
            "type": "TXT",
            "data": value,
            "ttl": max(60, min(int(ttl), 604800))
        }
        
        logging.info(f"Creating TXT record: {json.dumps(record_data)}")
        response = client.create_record(numeric_id, record_data)
        logging.info(f"Created record with ID: {response.get('id')}")
        return response
        
    except Exception as e:
        logging.error(f"Error creating record: {str(e)}")
        raise

def delete_txt_records(domain_id, host):
    try:
        client = get_client()
        numeric_id = get_domain_id(domain_id)
        
        domain_info = next((d for d in get_domains() if d['id'] == numeric_id), None)
        if not domain_info:
            raise ValueError(f"Domain with ID {numeric_id} not found")
            
        subdomain = extract_subdomain(host, domain_info['domain'])
        
        records = client.get_records(numeric_id)
        txt_records = [r for r in records if r['type'] == 'TXT' and r['host'] == subdomain]
        
        deleted = []
        for record in txt_records:
            client.delete_record(numeric_id, record['id'])
            deleted.append({
                'record_id': record['id'],
                'host': record['host'],
                'value': record['data']
            })
            logging.info(f"Deleted record {record['id']}")
            
        return {"success": True, "deleted": deleted, "count": len(deleted)}
        
    except Exception as e:
        logging.error(f"Error deleting records: {str(e)}")
        raise