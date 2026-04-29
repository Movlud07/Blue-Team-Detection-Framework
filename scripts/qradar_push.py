import os
import requests
import glob
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.environ.get("QRADAR_URL")
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")

def push_to_qradar():
    headers = {
        "SEC": QRADAR_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        # İNDİ ADI VƏ KODU BİRLİKDƏ GÖNDƏRİRİK
        # Amma fərqli endpoint istifadə edirik: saved_searches
        payload = {
            "name": f"API_Rule_{rule_name}",
            "query_expression": aql_query
        }
        
        # ENDPOINT DƏYİŞDİ: İndi birbaşa "Yadda saxlanılanlara" vururuq
        endpoint = f"{QRADAR_URL}/api/ariel/saved_searches"
        
        print(f"[{rule_name}] QRadar Saved Searches-ə əlavə edilir...")
        
        # Bu endpoint JSON formatını qəbul edir!
        response = requests.post(endpoint, headers=headers, json=payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu yükləndi: API_Rule_{rule_name}")
        elif response.status_code == 409:
            print(f"⚠️ Bu qayda artıq var, üzərinə yazılır: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
