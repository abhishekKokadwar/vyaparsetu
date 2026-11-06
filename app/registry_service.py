import pandas as pd
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data')

class RegistryService:
    def __init__(self):
        gst_path = os.path.join(DATA_DIR, 'mock_gstin_registry.csv')
        udyam_path = os.path.join(DATA_DIR, 'mock_udyam_registry.csv')
        self.gst_df = pd.read_csv(gst_path)
        self.udyam_df = pd.read_csv(udyam_path)

    @staticmethod
    def mask_gstin(gstin: str) -> str:
        """Masks central PAN characters for DPDP Act 2023 compliance"""
        if not gstin or len(gstin) != 15:
            return gstin
        return f"{gstin[:4]}XXXXXX{gstin[10:]}"

    @staticmethod
    def validate_gstin_format(gstin: str) -> bool:
        """
        Validates 15-character GSTIN structure.
        Accepts synthetic marker 'X' as 4th PAN character.
        """
        if not gstin:
            return False
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        return bool(re.match(pattern, gstin.strip().upper()))

    @staticmethod
    def validate_udyam_format(udyam_no: str) -> bool:
        """
        Validates Udyam registration structure: UDYAM-XX-00-XXXXXXX
        """
        if not udyam_no:
            return False
        pattern = r"^UDYAM-[A-Z]{2}-00-[0-9]{7}$"
        return bool(re.match(pattern, udyam_no.strip().upper()))

    def lookup_gstin(self, gstin: str):
        clean_gstin = gstin.strip().upper() if gstin else ""
        if not self.validate_gstin_format(clean_gstin):
            return {
                'found': False,
                'status': 'INVALID_FORMAT',
                'message': 'Invalid GSTIN format. Expected 15 alphanumeric characters.'
            }

        matches = self.gst_df[self.gst_df['gstin'] == clean_gstin]
        if matches.empty:
            return {
                'found': False,
                'status': 'NOT_FOUND',
                'message': 'GSTIN not found in the national registry.'
            }

        row = matches.iloc[0]
        status = row['status']
        is_active = (status.lower() == 'active')

        return {
            'found': True,
            'is_active': is_active,
            'gstin': row['gstin'],
            'gstin_masked': self.mask_gstin(row['gstin']),
            'legal_name': row['legal_name'],
            'trade_name': row['trade_name'],
            'constitution': row['constitution'],
            'principal_place_of_business': row['principal_place_of_business'],
            'state': row['state'],
            'registration_date': row['registration_date'],
            'status': status,
            'message': 'Active GSTIN verified successfully' if is_active else f"Warning: GSTIN status is {status}"
        }

    def lookup_udyam(self, udyam_no: str):
        clean_no = udyam_no.strip().upper() if udyam_no else ""
        if not self.validate_udyam_format(clean_no):
            return {
                'found': False,
                'status': 'INVALID_FORMAT',
                'message': 'Invalid Udyam format. Expected UDYAM-XX-00-XXXXXXX.'
            }

        matches = self.udyam_df[self.udyam_df['udyam_number'] == clean_no]
        if matches.empty:
            return {
                'found': False,
                'status': 'NOT_FOUND',
                'message': 'Udyam Registration Number not found in MSME registry.'
            }

        row = matches.iloc[0]
        return {
            'found': True,
            'is_active': True,
            'udyam_number': row['udyam_number'],
            'enterprise_name': row['enterprise_name'],
            'enterprise_type': row['enterprise_type'],
            'major_activity': row['major_activity'],
            'nic_description': row['nic_description'],
            'city': row['city'],
            'state': row['state'],
            'date_of_registration': row['date_of_registration'],
            'message': f"Verified {row['enterprise_type']} MSME enterprise"
        }

    def search_by_name(self, query: str):
        q = query.strip().lower()
        gst_matches = self.gst_df[
            self.gst_df['trade_name'].str.lower().str.contains(q, na=False) |
            self.gst_df['legal_name'].str.lower().str.contains(q, na=False)
        ].head(5)

        results = []
        for _, r in gst_matches.iterrows():
            results.append({
                'gstin': r['gstin'],
                'gstin_masked': self.mask_gstin(r['gstin']),
                'trade_name': r['trade_name'],
                'legal_name': r['legal_name'],
                'status': r['status'],
                'state': r['state']
            })
        return results

