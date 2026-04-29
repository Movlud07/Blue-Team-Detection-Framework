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
    print("--- 🔴 CRE QAYDALARI YENİLƏNİR (API UPDATE PROSESİ) ---")
    cre_files = glob.glob("../qradar_cre_rules/*.json")
    
    # 1. QRadar-dan mövcud qaydaları çəkirik
    print("🔄 QRadar-dan mövcud qaydaların siyahısı çəkilir...")
    get_endpoint = f"{QRADAR_URL}/api/analytics/rules"
    get_response = requests.get(get_endpoint, headers=headers, verify=False)
    
    if get_response.status_code != 200:
        print(f"❌ Qaydaları oxumaq mümkün olmadı: {get_response.status_code} - {get_response.text}")
        return
        
    existing_rules = get_response.json()
    rule_dict = {rule['name']: rule['id'] for rule in existing_rules}
    print(f"✅ Sistemdə qaydalar tapıldı. Yenilənməyə başlanılır...\n")
    
    cre_headers = headers.copy()
    cre_headers["Version"] = "12.0" 
    
    for file_path in cre_files:
        rule_name = os.path.basename(file_path).replace(".json", "")
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                rule_payload = json.load(f)
            except Exception:
                print(f"❌ JSON xətası: {rule_name}")
                continue
                
        payload_name = rule_payload.get('name')
        
        # 2. Əgər qaydanı QRadar-da tapdıqsa, UPDATE edirik
        if payload_name in rule_dict:
            rule_id = rule_dict[payload_name]
            rule_payload['id'] = rule_id # ID-ni json içinə əlavə edirik
            
            # Endpoint artıq /rules/{id} olaraq dəyişdi! Bu API POST (Update) qəbul edir!
            endpoint = f"{QRADAR_URL}/api/analytics/rules/{rule_id}"
            
            response = requests.post(endpoint, headers=cre_headers, json=rule_payload, verify=False)
            
            if response.status_code in [200, 201]:
                print(f"✅ Uğurlu Update: '{payload_name}' (ID: {rule_id}) GitHub-dan yeniləndi!")
            else:
                print(f"❌ Xəta Update ({response.status_code}): {response.text}")
        else:
            print(f"⚠️ DİQQƏT: '{payload_name}' tapılmadı! Zəhmət olmasa bu qaydanı əvvəlcə QRadar-da eyni adla manual yaradın.")

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
            
            time.sleep(5) 
            
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

if __name__ == "__main__":
    push_cre_rules()
    run_aql_hunts()
