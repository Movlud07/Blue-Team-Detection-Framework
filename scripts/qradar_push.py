import os
import requests
import glob
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# GitHub Secrets-dən gələcək gizli məlumatlar
QRADAR_URL = os.environ.get("QRADAR_URL")
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")

def push_to_qradar():
    headers = {
        "SEC": QRADAR_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # qradar_rules qovluğundakı bütün .aql fayllarını tapır
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read()
            
        # DÜZƏLİŞ BURADADIR: QRadar yalnız query_expression qəbul edir!
        payload = {
            "query_expression": aql_query
        }
        
        endpoint = f"{QRADAR_URL}/api/ariel/searches"
        
        print(f"[{rule_name}] QRadar-a göndərilir...")
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
