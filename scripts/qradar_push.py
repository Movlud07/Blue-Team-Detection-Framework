import os
import requests
import glob
import urllib3

# SSL xəbərdarlıqlarını söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL-i təmizləyirik (sondakı slash xətasına son)
raw_url = os.environ.get("QRADAR_URL", "")
QRADAR_URL = raw_url.rstrip('/') 
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")

def push_to_qradar():
    # 100% qarantili headers
    headers = {
        "SEC": QRADAR_TOKEN,
        "Accept": "application/json"
    }
    
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        # QRadar-ın Saved Search yaratmaq üçün istədiyi parametrlər
        payload = {
            "name": f"API_Rule_{rule_name}",
            "query_expression": aql_query
        }
        
        # Sənin curl ilə cavab aldığın o tam doğru ünvan
        endpoint = f"{QRADAR_URL}/api/ariel/saved_searches"
        
        print(f"[{rule_name}] QRadar-a yüklənir...")
        
        # DÜZƏLİŞ: json=payload YERİNƏ data=payload istifadə edirik!
        # Bu, məlumatı form-data kimi göndərir və QRadar-ın inadını qırır.
        response = requests.post(endpoint, headers=headers, data=payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu: API_Rule_{rule_name}")
        elif response.status_code == 409:
            print(f"⚠️ Artıq mövcuddur: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
