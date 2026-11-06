from app.catalog_engine import CatalogEngine

class AdvisorEngine:
    def __init__(self, catalog: CatalogEngine):
        self.catalog = catalog

    def recommend(self, profile: dict):
        """
        profile: {
            'business_type': 'Kirana / Retail' | 'Clinic' | 'CA / Legal Firm' | 'Restaurant Chain' | 'Manufacturing Unit' | other,
            'segment': 'micro' | 'prof' | 'multi' | 'mfg' (optional, derived if not given),
            'city_tier': 1 | 2,
            'employee_count': int,
            'num_sites': int,
            'has_gstin': bool,
            'current_spend': int (optional),
            'preferred_language': 'en' | 'hi'
        }
        """
        btype = profile.get('business_type', '').lower()
        tier = int(profile.get('city_tier', 1))
        employees = int(profile.get('employee_count', 2))
        sites = int(profile.get('num_sites', 1))
        has_gstin = bool(profile.get('has_gstin', False))
        lang = profile.get('preferred_language', 'en')

        # 1. Infer Segment
        segment = profile.get('segment')
        if not segment:
            if sites > 1 or 'chain' in btype or 'retail store' in btype:
                segment = 'multi'
            elif any(k in btype for k in ['factory', 'mfg', 'manufactur', 'textile', 'auto']):
                segment = 'mfg'
            elif any(k in btype for k in ['clinic', 'doctor', 'hospital', 'ca', 'law', 'consult', 'coaching']):
                segment = 'prof'
            else:
                segment = 'micro'

        selected_pids = []
        quantities = {}
        reasoning_points_en = []
        reasoning_points_hi = []

        # 2. Segment-specific bundle logic adhering strictly to catalogue rules
        if segment == 'micro':
            bundle_name_en = "Vyapar Booster Pack (Kirana & Micro-Enterprise)"
            bundle_name_hi = "व्यापार बूस्टर पैक (किराना और सूक्ष्म उद्यम)"

            # Primary connectivity: Biz Fibre 100 or AirFiber 100
            if tier == 2 or 'kiosk' in btype:
                selected_pids.append('P04') # 5G AirFiber 100
                quantities['P04'] = 1
                reasoning_points_en.append("⚡ Rapid 2-day install with Biz 5G AirFiber 100 for zero-lag UPI QR payments and billing.")
                reasoning_points_hi.append("⚡ बिज़ 5G एयरफ़ाइबर 100 के साथ मात्र 2 दिन में तेज़ इंस्टॉलेशन — UPI और बिलिंग में शून्य रुकावट।")
            else:
                selected_pids.append('P01') # Biz Fibre 100
                quantities['P01'] = 1
                reasoning_points_en.append("⚡ Reliable Biz Fibre 100 Mbps with unlimited business data to ensure customer billing never stops.")
                reasoning_points_hi.append("⚡ बिज़ फ़ाइबर 100 Mbps अनलिमिटेड डेटा — ग्राहकों के बिलिंग काउंटर पर निर्बाध स्पीड।")

            # Productivity: Cloud POS & Billing
            selected_pids.append('P19')
            quantities['P19'] = 1
            reasoning_points_en.append("📱 Cloud POS & Billing with inventory management on mobile, replacing paper khata.")
            reasoning_points_hi.append("📱 मोबाइल पर क्लाउड POS और डिजिटल बिलिंग — पुराने बही-खाते से पूर्ण मुक्ति।")

            # Communication / Customer reach
            if has_gstin:
                selected_pids.append('P15') # WhatsApp Business API
                quantities['P15'] = 1
                reasoning_points_en.append("💬 Official WhatsApp Business API to send offers, bills, and payment receipts directly to customers.")
                reasoning_points_hi.append("💬 आधिकारिक व्हाट्सएप बिज़नेस API — ग्राहकों को सीधे ऑफ़र, रसीद और पेमेंट लिंक भेजें।")
            else:
                selected_pids.append('P07') # Business Postpaid 299
                quantities['P07'] = 1
                reasoning_points_en.append("📞 Dedicated Business Postpaid SIM with unlimited calling for owner and store deliveries.")
                reasoning_points_hi.append("📞 असीमित कॉलिंग वाला बिज़नेस पोस्टपेड सिम — डिलीवरी और कस्टमर सपोर्ट के लिए।")

            # IoT: Cloud CCTV
            selected_pids.append('P23')
            quantities['P23'] = 1
            reasoning_points_en.append("📹 Cloud CCTV for 24/7 store surveillance with mobile live-stream viewing.")
            reasoning_points_hi.append("📹 क्लाउड CCTV कैमरा — मोबाइल पर 24/7 दुकान की लाइव निगरानी और सुरक्षा।")

        elif segment == 'prof':
            bundle_name_en = "Vyapar Professional Suite (Clinics, CAs & Firms)"
            bundle_name_hi = "व्यापार प्रोफ़ेशनल सूट (क्लीनिक, सीए एवं कार्यालय)"

            # High-speed reliable connectivity
            selected_pids.append('P02') # Biz Fibre 300
            quantities['P02'] = 1
            reasoning_points_en.append("🚀 High-speed Biz Fibre 300 Mbps supporting multiple consultations, webinars, and large file syncs.")
            reasoning_points_hi.append("🚀 बिज़ फ़ाइबर 300 Mbps सुपरफ़ास्ट स्पीड — वीडियो मीटिंग्स और बड़ी फ़ाइलों के तेज़ ट्रांसफर के लिए।")

            # Static IP for secure server access / CCTV
            selected_pids.append('P11')
            quantities['P11'] = 1
            reasoning_points_en.append("🌐 Dedicated Static IP for secure ERP/Tally remote access and biometric security.")
            reasoning_points_hi.append("🌐 सुरक्षित स्टैटिक IP — टैली और ईआरपी सर्वर के सुरक्षित रिमोट एक्सेस के लिए।")

            # Cloud Email & Office Suite
            selected_pids.append('P16')
            email_seats = max(2, employees)
            quantities['P16'] = email_seats
            reasoning_points_en.append(f"📧 Professional custom-domain Cloud Email & Office for {email_seats} team members.")
            reasoning_points_hi.append(f"📧 {email_seats} सदस्यों के लिए प्रोफ़ेशनल डोमेन ईमेल और क्लाउड ऑफिस सुइट।")

            # Cloud Backup 1TB
            selected_pids.append('P17')
            quantities['P17'] = 1
            reasoning_points_en.append("🔒 Automated 1 TB Cloud Backup to safeguard critical patient records and tax filings against ransomware.")
            reasoning_points_hi.append("🔒 1 TB ऑटोमैटिक क्लाउड बैकअप — महत्वपूर्ण वित्तीय डेटा और रिकॉर्ड्स की फुल सुरक्षा।")

            # Secure Wi-Fi with Guest Network
            selected_pids.append('P22')
            quantities['P22'] = 1
            reasoning_points_en.append("📶 Isolated Secure Wi-Fi with separate Guest Network for waiting visitors.")
            reasoning_points_hi.append("📶 सिक्योर वाई-फ़ाई — ग्राहकों और आगंतुकों के लिए अलग सुरक्षित गेस्ट नेटवर्क।")

        elif segment == 'multi':
            bundle_name_en = "Vyapar Multi-Site Connect (Retail Chains & Multi-Store)"
            bundle_name_hi = "व्यापार मल्टी-साइट कनेक्ट (रिटेल चेन और शाखाएं)"

            # Base connectivity across sites
            selected_pids.append('P02') # Biz Fibre 300
            quantities['P02'] = sites
            reasoning_points_en.append(f"🏢 Enterprise Biz Fibre 300 deployed across all {sites} retail branches under a single unified bill.")
            reasoning_points_hi.append(f"🏢 सभी {sites} शाखाओं में बिज़ फ़ाइबर 300 — सभी का एक ही एकीकृत बिल।")

            # Backup 4G/5G Failover
            selected_pids.append('P09')
            quantities['P09'] = sites
            reasoning_points_en.append("🔄 Automatic 4G/5G Failover at every location to guarantee 99.9% POS and transaction uptime.")
            reasoning_points_hi.append("🔄 ऑटोमैटिक 4G/5G बैकअप — इंटरनेट कटने पर भी बिलिंग काउंटर कभी बंद नहीं होगा।")

            # Managed SD-WAN (if GST available)
            if has_gstin and sites >= 2:
                selected_pids.append('P10')
                quantities['P10'] = 1
                reasoning_points_en.append("🌐 Managed SD-WAN uniting all branches with encrypted intranet and centralized IT control.")
                reasoning_points_hi.append("🌐 मैनेज्ड SD-WAN — सभी शाखाओं को एक सुरक्षित प्राइवेट नेटवर्क से जोड़ें।")

            # Centralized Cloud CCTV
            selected_pids.append('P23')
            quantities['P23'] = sites * 2
            reasoning_points_en.append(f"📹 Centralized Cloud CCTV ({sites * 2} cameras) monitored from owner's smartphone.")
            reasoning_points_hi.append(f"📹 सेंट्रलाइज़्ड क्लाउड CCTV — एक ही स्क्रीन पर सभी शाखाओं की लाइव निगरानी।")

            # Toll-Free or SIP
            if has_gstin:
                selected_pids.append('P13') # Toll-free
                quantities['P13'] = 1
                reasoning_points_en.append("📞 Dedicated 1800 Toll-Free Customer Care Number for brand trust and customer support.")
                reasoning_points_hi.append("📞 1800 टोल-फ़्री कस्टमर केयर नंबर — ग्राहकों के विश्वास और सपोर्ट के लिए।")

        else: # Small Manufacturers ('mfg')
            bundle_name_en = "Vyapar Industry Pro (Small Manufacturing & Plants)"
            bundle_name_hi = "व्यापार इंडस्ट्री प्रो (लघु निर्माण और उद्योग)"

            if has_gstin:
                selected_pids.append('P05') # Internet Leased Line 20
                quantities['P05'] = 1
                reasoning_points_en.append("🏭 1:1 Dedicated Internet Leased Line (20 Mbps) with 99.9% SLA and enterprise latency.")
                reasoning_points_hi.append("🏭 1:1 डेडिकेटेड इंटरनेट लीज्ड लाइन — 99.9% अपटाइम SLA के साथ।")

                selected_pids.append('P21') # Managed Firewall
                quantities['P21'] = 1
                reasoning_points_en.append("🛡️ Enterprise Managed Firewall blocking ransomware and unauthorized factory network intrusion.")
                reasoning_points_hi.append("🛡️ एंटरप्राइज फ़ायरवॉल — फ़ैक्टरी नेटवर्क और डेटा की साइबर सुरक्षा।")

                selected_pids.append('P24') # Machine Monitoring IoT
                quantities['P24'] = min(employees, 5)
                reasoning_points_en.append(f"⚙️ Machine Monitoring IoT sensors ({quantities['P24']} units) for predictive maintenance.")
                reasoning_points_hi.append(f"⚙️ मशीन मॉनिटरिंग IoT सेंसर्स — मशीनों के अपटाइम और बिजली खपत की रियल-टाइम रिपोर्ट।")
            else:
                selected_pids.append('P03' if tier == 1 else 'P02')
                quantities[selected_pids[0]] = 1
                reasoning_points_en.append("🚀 High-throughput Business Fibre for CAD designs, ERP sync, and plant operations.")
                reasoning_points_hi.append("🚀 हाई-स्पीड बिज़नेस फ़ाइबर — ERP और फ़ैक्टरी ऑपरेशन्स के लिए।")

            selected_pids.append('P17') # Cloud Backup 1TB
            quantities['P17'] = 1
            reasoning_points_en.append("💾 Automated Cloud Backup safeguarding design blueprints, GST records, and ERP backups.")
            reasoning_points_hi.append("💾 स्वचालित क्लाउड बैकअप — डिज़ाइन और टैक्स फाइलों की सुरक्षित स्टोरेज।")

        # 3. Validate against catalogue rules
        is_valid, validation_errors = self.catalog.validate_selection(
            selected_pids,
            city_tier=tier,
            employees=employees,
            sites=sites,
            has_gstin=has_gstin
        )

        # 4. Calculate detailed pricing
        items_payload = [{'product_id': pid, 'quantity': quantities.get(pid, 1)} for pid in selected_pids]
        pricing = self.catalog.calculate_bundle_pricing(items_payload)

        # 5. Calculate Savings vs. Multiple Unorganized Vendors
        unorganized_cost = int(pricing['monthly_total_inr'] * 1.45)
        monthly_savings = unorganized_cost - pricing['monthly_total_inr']
        annual_savings = monthly_savings * 12

        return {
            'segment': segment,
            'bundle_name': bundle_name_hi if lang == 'hi' else bundle_name_en,
            'bundle_name_en': bundle_name_en,
            'bundle_name_hi': bundle_name_hi,
            'selected_product_ids': selected_pids,
            'pricing': pricing,
            'savings': {
                'unorganized_cost_inr': unorganized_cost,
                'monthly_savings_inr': monthly_savings,
                'annual_savings_inr': annual_savings,
                'savings_percent': 31
            },
            'reasoning': reasoning_points_hi if lang == 'hi' else reasoning_points_en,
            'reasoning_en': reasoning_points_en,
            'reasoning_hi': reasoning_points_hi,
            'is_compliant': is_valid,
            'validation_errors': validation_errors
        }

