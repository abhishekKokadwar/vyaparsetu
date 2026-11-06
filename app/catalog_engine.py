import pandas as pd
import os
import math

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'product_catalogue.csv')

class CatalogEngine:
    def __init__(self):
        self.df = pd.read_csv(CATALOG_PATH)
        self.products = self._load_products()

    def _load_products(self):
        prods = {}
        for _, row in self.df.iterrows():
            req_one = []
            if pd.notna(row['requires_one_of']) and str(row['requires_one_of']).strip() != '':
                req_one = [x.strip() for x in str(row['requires_one_of']).split('|')]
            
            target_segs = []
            if pd.notna(row['target_segments']):
                target_segs = [x.strip() for x in str(row['target_segments']).split(';')]

            prods[row['product_id']] = {
                'product_id': row['product_id'],
                'category': row['category'],
                'product_name': row['product_name'],
                'description': row['description'],
                'unit': row['unit'],
                'price_min_inr_per_month': int(row['price_min_inr_per_month']),
                'price_max_inr_per_month': int(row['price_max_inr_per_month']),
                'one_time_setup_inr': int(row['one_time_setup_inr']),
                'min_contract_months': int(row['min_contract_months']),
                'available_city_tiers': [int(x) for x in str(row['available_city_tiers']).split(';')],
                'min_employees': int(row['min_employees']) if pd.notna(row['min_employees']) else 1,
                'min_sites': int(row['min_sites']) if pd.notna(row['min_sites']) else 1,
                'requires_gstin': str(row['requires_gstin']).upper() == 'Y',
                'requires_one_of': req_one,
                'typical_install_days': int(row['typical_install_days']),
                'target_segments': target_segs
            }
        return prods

    def get_all(self):
        return list(self.products.values())

    def get_product(self, product_id):
        return self.products.get(product_id)

    def validate_selection(self, selected_product_ids, city_tier=1, employees=1, sites=1, has_gstin=False):
        """
        Validates whether selected products satisfy catalogue constraints.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        selected_set = set(selected_product_ids)

        for pid in selected_product_ids:
            p = self.products.get(pid)
            if not p:
                errors.append(f"Unknown product {pid}")
                continue

            # GSTIN requirement
            if p['requires_gstin'] and not has_gstin:
                errors.append(f"'{p['product_name']}' requires an active GSTIN, which this business does not have.")

            # City tier
            if city_tier not in p['available_city_tiers']:
                errors.append(f"'{p['product_name']}' is not available in City Tier {city_tier}.")

            # Min employees
            if employees < p['min_employees']:
                errors.append(f"'{p['product_name']}' requires at least {p['min_employees']} employees (business has {employees}).")

            # Min sites
            if sites < p['min_sites']:
                errors.append(f"'{p['product_name']}' requires at least {p['min_sites']} sites (business has {sites}).")

            # Dependency checks (requires_one_of)
            if p['requires_one_of']:
                has_dep = any(dep in selected_set for dep in p['requires_one_of'])
                if not has_dep:
                    dep_names = [self.products[d]['product_name'] for d in p['requires_one_of'] if d in self.products]
                    errors.append(f"'{p['product_name']}' requires at least one of base connectivity: {', '.join(dep_names)}")

        return (len(errors) == 0, errors)

    def calculate_bundle_pricing(self, items):
        """
        items: list of dicts [{'product_id': 'P01', 'quantity': 1}, ...]
        Returns {monthly_total, setup_total, min_contract_months, max_install_days, items_detail}
        """
        monthly_total = 0
        setup_total = 0
        max_contract = 1
        max_install_days = 1
        details = []

        for it in items:
            pid = it['product_id']
            qty = it.get('quantity', 1)
            p = self.products.get(pid)
            if not p:
                continue
            
            # Using price_min as standard baseline offer
            item_monthly = p['price_min_inr_per_month'] * qty
            item_setup = p['one_time_setup_inr'] * (1 if p['one_time_setup_inr'] > 0 else 0)
            
            monthly_total += item_monthly
            setup_total += item_setup
            max_contract = max(max_contract, p['min_contract_months'])
            max_install_days = max(max_install_days, p['typical_install_days'])

            details.append({
                'product_id': pid,
                'product_name': p['product_name'],
                'category': p['category'],
                'quantity': qty,
                'unit_price': p['price_min_inr_per_month'],
                'total_monthly': item_monthly,
                'setup_fee': item_setup,
                'install_days': p['typical_install_days']
            })

        return {
            'monthly_total_inr': monthly_total,
            'setup_total_inr': setup_total,
            'contract_months': max_contract,
            'estimated_install_days': max_install_days,
            'items': details
        }

