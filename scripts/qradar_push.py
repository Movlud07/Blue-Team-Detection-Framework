import os
import requests
import glob
import json
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.environ.get("QRADAR_URL", "").rstrip('/')
QRADAR_TOKEN = os.environ.get("QRADAR_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

headers = {
    "SEC": QRADAR_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def send_telegram_alert(rule_name, event_count):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"🚨 *SOC XƏBƏRDARLIĞI (AQL Hunt)* 🚨\n\n🎯 *Tətiklənən Qayda:* {rule_name}\n📊 *Tapılan Hadisə Sayı:* {event_count}\n🔍 *Sistem:* DC-01/DC-02 Logları yoxlanıldı.\n\nTəcili QRadar Ariel bazasını yoxlayın!"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def push_cre_rules():
    print("--- 🔴 CRE QAYDALARI YÜKLƏNİR (OFFENSE YARADANLAR) ---")
    cre_files = glob.glob("../qradar_cre_rules/*.json")
    
    # QRadar API Versiyasını qeyd edirik
    cre_headers = headers.copy()
    cre_headers["Version"] = "16.0" 
    
    for file_path in cre_files:
        rule_name = os.path.basename(file_path).replace(".json", "")
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                rule_payload = json.load(f)
            except Exception:
                print(f"❌ JSON xətası: {rule_name}")
                continue
                
        endpoint = f"{QRADAR_URL}/api/analytics/rules"
        response = requests.post(endpoint, headers=cre_headers, json=rule_payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu (CRE): '{rule_name}' interfeysdə yaradıldı!")
        elif response.status_code == 409:
            print(f"⚠️ Artıq mövcuddur: {rule_name}")
        else:
            print(f"❌ Xəta ({response.status_code}): {response.text}")

def run_aql_hunts():
    print("\n--- 🔵 AQL HUNT İCRA EDİLİR (TELEGRAM XƏBƏRDARLIQLI) ---")
    aql_headers = {"SEC": QRADAR_TOKEN, "Accept": "application/json"}
    aql_files = glob.glob("../qradar_aql_rules/*.aql")
    
    for file_path in aql_files:
        rule_name = os.path.basename(file_path).replace(".aql", "")
        with open(file_path, "r", encoding="utf-8") as f:
            aql_query = f.read().strip()
            
        endpoint = f"{QRADAR_URL}/api/ariel/searches"
        response = requests.post(endpoint, headers=aql_headers, params={"query_expression": aql_query}, verify=False)
        
        if response.status_code in [200, 201]:
            search_id = response.json().get("search_id")
            print(f"⏳ Axtarış başladı: {rule_name}. Nəticə gözlənilir...")
            
            time.sleep(5) # QRadar-ın axtarışı bitirməsi üçün 5 saniyə vaxt veririk
            
            res_endp = f"{QRADAR_URL}/api/ariel/searches/{search_id}/results"
            res = requests.get(res_endp, headers=aql_headers, verify=False)
            
            if res.status_code == 200:
                events = res.json().get('events', [])
                if len(events) > 0:
                    print(f"🚨 TƏHDİD TAPILDI: {rule_name}! Telegram-a göndərilir...")
                    send_telegram_alert(rule_name, len(events))
                else:
                    print(f"✅ Təmizdir: {rule_name} (Təhdid yoxdur)")
        else:
            print(f"❌ Xəta: {rule_name} icra edilmədi.")

# BAX BU HİSSƏ ÇOX VACİBDİR! SKRİPTİ İŞƏ SALAN BLOK:
if __name__ == "__main__":
    push_cre_rules()
    run_aql_hunts()
