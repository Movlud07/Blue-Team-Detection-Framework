def push_cre_rules():
    print("--- 🔴 CRE QAYDALARI YÜKLƏNİR (OFFENSE YARADANLAR) ---")
    cre_files = glob.glob("../qradar_cre_rules/*.json")
    
    # QRadar API Versiyasını qeyd edirik (Bu, 404-ün qarşısını ala bilər)
    cre_headers = headers.copy()
    cre_headers["Version"] = "12.0" # Və ya QRadar versiyana uyğun 15.0
    
    for file_path in cre_files:
        rule_name = os.path.basename(file_path).replace(".json", "")
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                rule_payload = json.load(f)
            except Exception:
                print(f"❌ JSON xətası: {rule_name}")
                continue
                
        # QEYD: Bəzi versiyalarda endpoint sonuna slash istəyir
        endpoint = f"{QRADAR_URL}/api/analytics/rules"
        response = requests.post(endpoint, headers=cre_headers, json=rule_payload, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"✅ Uğurlu (CRE): '{rule_name}' interfeysdə yaradıldı!")
        elif response.status_code == 409:
            print(f"⚠️ Artıq mövcuddur: {rule_name}")
        else:
            # Buranı daha detallı çıxarırıq ki, problemi görək
            print(f"❌ Xəta ({response.status_code}): {response.text}")
