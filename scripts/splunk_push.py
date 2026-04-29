import os
import requests
import glob
import urllib3

# SIEM lablarında SSL xətası almamaq üçün xəbərdarlıqları söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# GitHub Secrets-dən gələcək gizli məlumatlar
SPLUNK_URL = os.environ.get("SPLUNK_URL") # Məsələn: https://192.168.1.50:8089
SPLUNK_TOKEN = os.environ.get("SPLUNK_TOKEN")

def push_to_splunk():
    headers = {
        "Authorization": f"Bearer {SPLUNK_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # splunk_rules qovluğundakı bütün .spl fayllarını tapır
    rule_files = glob.glob("../splunk_rules/*.spl")
    
    for file_path in rule_files:
        rule_name = os.path.basename(file_path).replace(".spl", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            spl_query = f.read()
            
        # Splunk API-yə göndəriləcək məlumatlar (Payload)
        payload = {
            "name": rule_name,
            "search": spl_query,
            "is_scheduled": "1",
            "cron_schedule": "*/5 * * * *" # Hər 5 dəqiqədən bir yoxla
        }
        
        endpoint = f"{SPLUNK_URL}/services/saved/searches"
        
        print(f"[{rule_name}] Splunk-a göndərilir...")
        response = requests.post(endpoint, headers=headers, data=payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu: {rule_name}")
        elif response.status_code == 409:
            print(f"⚠️ Bu qayda artıq var: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

if __name__ == "__main__":
    push_to_splunk()
