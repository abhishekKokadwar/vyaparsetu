import pandas as pd
import os
import re
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data')

class RegistryService:
    """
    Phase 4: Real-time National Registry Cross-Verification Engine.
    Provides sub-millisecond lookups for mock GSTIN and Udyam national databases,
    format validators compliant with synthetic hackathon data ('X' marker, '00' district),
    and DPDP Act 2023 PII masking.
    """
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        gst_path = os.path.join(self.data_dir, 'mock_gstin_registry.csv')
        udyam_path = os.path.join(self.data_dir, 'mock_udyam_registry.csv')
        
        self.gst_df = pd.read_csv(gst_path)
        self.udyam_df = pd.read_csv(udyam_path)
        
        # Build in-memory hash indexes for O(1) lookups (<1ms)
        self._gst_index: Dict[str, dict] = {}
        self._udyam_index: Dict[str, dict] = {}
        self._build_indexes()

    def _build_indexes(self):
        """Constructs fast hash tables for national registry lookups"""
        for _, row in self.gst_df.iterrows():
            g = str(row['gstin']).strip().upper()
            self._gst_index[g] = {
                'gstin': g,
                'legal_name': str(row['legal_name']).strip(),
                'trade_name': str(row['trade_name']).strip(),
                'constitution': str(row['constitution']).strip(),
                'principal_place_of_business': str(row['principal_place_of_business']).strip(),
                'state': str(row['state']).strip(),
                'registration_date': str(row['registration_date']).strip(),
                'status': str(row['status']).strip()
            }

        for _, row in self.udyam_df.iterrows():
            u = str(row['udyam_number']).strip().upper()
            self._udyam_index[u] = {
                'udyam_number': u,
                'enterprise_name': str(row['enterprise_name']).strip(),
                'enterprise_type': str(row['enterprise_type']).strip(),
                'major_activity': str(row['major_activity']).strip(),
                'nic_description': str(row['nic_description']).strip(),
                'city': str(row['city']).strip(),
                'state': str(row['state']).strip(),
                'date_of_registration': str(row['date_of_registration']).strip()
            }

    @staticmethod
    def mask_gstin(gstin: str) -> str:
        """
        Masks central 6 characters of the embedded PAN for DPDP Act 2023 compliance.
        Format: 2-digit state code + 2 PAN chars + XXXXXX + last 2 PAN chars + entity suffix.
        Example: '37IHKXV5167L1ZS' -> '37IHXXXXXX67L1ZS'
        """
        if not gstin or len(gstin) != 15:
            return gstin
        clean = gstin.strip().upper()
        return f"{clean[:4]}XXXXXX{clean[10:]}"

    @staticmethod
    def mask_pan(pan: str) -> str:
        """Masks central 6 characters of PAN: 'ABCDE1234F' -> 'ABXXXXXX4F'"""
        if not pan or len(pan) != 10:
            return pan
        clean = pan.strip().upper()
        return f"{clean[:2]}XXXXXX{clean[8:]}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Masks central digits of contact numbers: '+91 98450 12345' -> '+91 98XXXXXX45' or '98XXXXXX45'"""
        if not phone or len(str(phone).strip()) < 10:
            return str(phone)
        digits = re.sub(r'[^0-9]', '', str(phone))
        if len(digits) >= 10:
            last10 = digits[-10:]
            prefix = "+91 " if len(digits) > 10 else ""
            return f"{prefix}{last10[:2]}XXXXXX{last10[8:]}"
        return str(phone)

    @staticmethod
    def validate_gstin_format(gstin: str) -> bool:
        """
        Validates 15-character GSTIN structure:
        - 2 digits (State code)
        - 5 letters (PAN letters, accepting 'X' as 4th character for synthetic dataset)
        - 4 digits (PAN numbers)
        - 1 letter (PAN checksum)
        - 1 alphanumeric entity count
        - 'Z' default character
        - 1 alphanumeric checksum
        """
        if not gstin:
            return False
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        return bool(re.match(pattern, gstin.strip().upper()))

    @staticmethod
    def validate_udyam_format(udyam_no: str) -> bool:
        """
        Validates Udyam registration structure: UDYAM-XX-00-XXXXXXX
        (Accepts '00' synthetic district code).
        """
        if not udyam_no:
            return False
        pattern = r"^UDYAM-[A-Z]{2}-00-[0-9]{7}$"
        return bool(re.match(pattern, udyam_no.strip().upper()))

    def lookup_gstin(self, gstin: str) -> dict:
        """Sub-millisecond GSTIN lookup with status verification and PII masking"""
        clean_gstin = gstin.strip().upper() if gstin else ""
        if not self.validate_gstin_format(clean_gstin):
            return {
                'found': False,
                'status': 'INVALID_FORMAT',
                'message': 'Invalid GSTIN format. Expected 15 alphanumeric characters adhering to GST structure.'
            }

        rec = self._gst_index.get(clean_gstin)
        if not rec:
            return {
                'found': False,
                'status': 'NOT_FOUND',
                'message': f"GSTIN '{clean_gstin}' was not found in the national GSTN registry."
            }

        status = rec['status']
        is_active = (status.lower() == 'active')

        return {
            'found': True,
            'is_active': is_active,
            'gstin': rec['gstin'],
            'gstin_masked': self.mask_gstin(rec['gstin']),
            'legal_name': rec['legal_name'],
            'trade_name': rec['trade_name'],
            'constitution': rec['constitution'],
            'principal_place_of_business': rec['principal_place_of_business'],
            'state': rec['state'],
            'registration_date': rec['registration_date'],
            'status': status,
            'message': 'Active GSTIN verified successfully' if is_active else f"Warning: GSTIN status is '{status.upper()}' (Inactive/Cancelled)"
        }

    def lookup_udyam(self, udyam_no: str) -> dict:
        """Sub-millisecond Udyam MSME lookup with classification details"""
        clean_no = udyam_no.strip().upper() if udyam_no else ""
        if not self.validate_udyam_format(clean_no):
            return {
                'found': False,
                'status': 'INVALID_FORMAT',
                'message': 'Invalid Udyam format. Expected format: UDYAM-XX-00-XXXXXXX.'
            }

        rec = self._udyam_index.get(clean_no)
        if not rec:
            return {
                'found': False,
                'status': 'NOT_FOUND',
                'message': f"Udyam registration '{clean_no}' was not found in the MSME national portal."
            }

        return {
            'found': True,
            'is_active': True,
            'udyam_number': rec['udyam_number'],
            'enterprise_name': rec['enterprise_name'],
            'enterprise_type': rec['enterprise_type'],
            'major_activity': rec['major_activity'],
            'nic_description': rec['nic_description'],
            'city': rec['city'],
            'state': rec['state'],
            'date_of_registration': rec['date_of_registration'],
            'message': f"Verified {rec['enterprise_type']} MSME enterprise ({rec['major_activity']})"
        }

    def search_by_name(self, query: str, limit: int = 5) -> List[dict]:
        """Fast fuzzy/substring search over registered businesses"""
        q = query.strip().lower()
        if not q or len(q) < 2:
            return []

        results = []
        for g, rec in self._gst_index.items():
            if q in rec['trade_name'].lower() or q in rec['legal_name'].lower():
                results.append({
                    'gstin': rec['gstin'],
                    'gstin_masked': self.mask_gstin(rec['gstin']),
                    'trade_name': rec['trade_name'],
                    'legal_name': rec['legal_name'],
                    'status': rec['status'],
                    'state': rec['state']
                })
                if len(results) >= limit:
                    break
        return results
