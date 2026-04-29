import os
import requests
import glob
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.environ.get("QRADAR_URL")
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")

def push_to_qradar():
    # 100% qarantili headers
    headers = {
        "SEC": QRADAR_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Version": "19.0" # Ən son stabil API versiyasını məcburi edirik
    }
    
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        # Saved search üçün lazımi payload
        payload = {
            "name": f"API_Rule_{rule_name}",
            "query_expression": aql_query
        }
        
        # ƏN VACİB DƏYİŞİKLİK: Endpoint yolunu dəyişdik
        # /api/ariel/saved_searches -> /api/search/saved_searches
        endpoint = f"{QRADAR_URL}/api/search/saved_searches"
        
        print(f"[{rule_name}] QRadar siyahısına əlavə edilir...")
        
        # Məlumatı JSON bədəni kimi (json=payload) göndəririk
        response = requests.post(endpoint, headers=headers, json=payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu: API_Rule_{rule_name}")
        elif response.status_code == 409:
            print(f"⚠️ Bu adda qayda artıq var: {rule_name}")
        else:
            # Əgər hələ də xəta versə, mənə səbəbini göstərəcək
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
