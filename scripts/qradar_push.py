import os
import requests
import glob
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.environ.get("QRADAR_URL")
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")

def push_to_qradar():
    # Versiyanı 12.0 olaraq məcburi təyin edirik ki, 404 xətası verməsin
    headers = {
        "SEC": QRADAR_TOKEN,
        "Accept": "application/json",
        "Version": "12.0" 
    }
    
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        # QRadar bəzən JSON body-ni rədd edir, ona görə məlumatı PARAMS kimi göndəririk
        payload = {
            "name": f"API_Rule_{rule_name}",
            "query_expression": aql_query
        }
        
        endpoint = f"{QRADAR_URL}/api/ariel/saved_searches"
        
        print(f"[{rule_name}] Siyahıya əlavə edilir...")
        
        # ƏN KRİTİK DÜZƏLİŞ: json=payload YOX, params=payload istifadə edirik
        response = requests.post(endpoint, headers=headers, params=payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu: API_Rule_{rule_name}")
        elif response.status_code == 409:
            print(f"⚠️ Artıq var: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
