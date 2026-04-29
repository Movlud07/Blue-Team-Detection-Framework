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
    # 100% qarantili headers - Content-Type əlavə olundu
    headers = {
        "SEC": QRADAR_TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    rule_files = glob.glob("../qradar_rules/*.aql")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        # QRadar-ın AQL icrası üçün istədiyi parametrlər
        payload = {
            "query_expression": aql_query
        }
        
        # Doğru endpoint: Mövcud olmayan saved_searches yerinə birbaşa searches
        endpoint = f"{QRADAR_URL}/api/ariel/searches"
        
        print(f"[{rule_name}] QRadar-a göndərilir...")
        
        # DÜZƏLİŞ: data=payload YERİNƏ json=payload istifadə edirik!
        response = requests.post(endpoint, headers=headers, json=payload, verify=False)
        
        if response.status_code in [200, 201]:
            # Uğurlu olduqda QRadar bizə bir search_id qaytarır
            response_data = response.json()
            search_id = response_data.get("search_id", "Bilinmir")
            print(f"✅ Uğurlu: {rule_name} (Search ID: {search_id})")
        elif response.status_code == 409:
            print(f"⚠️ Artıq mövcuddur: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_qradar()
