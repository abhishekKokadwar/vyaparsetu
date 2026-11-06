import pandas as pd
import os
from typing import List, Dict, Tuple, Optional, Set

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'product_catalogue.csv')

class CatalogEngine:
    """
    Phase 2: Deterministic Catalog & Dynamic Pricing Engine.
    Evaluates business rules, resolves dependency graphs, computes transparent
    single-bill bundle quotations, and quantifies savings vs. fragmented vendors.
    """
    def __init__(self, csv_path: str = CATALOG_PATH):
        self.csv_path = csv_path
        self.df = pd.read_csv(self.csv_path)
        self.products: Dict[str, dict] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.segment_index: Dict[str, List[str]] = {}
        self._build_indexes()

    def _build_indexes(self):
        """Constructs in-memory indexes for sub-millisecond retrieval and validation"""
        for _, row in self.df.iterrows():
            pid = str(row['product_id']).strip()
            
            # Dependencies
            req_one = []
            if pd.notna(row['requires_one_of']) and str(row['requires_one_of']).strip() != '':
                req_one = [x.strip() for x in str(row['requires_one_of']).split('|')]
            
            # Target segments
            target_segs = []
            if pd.notna(row['target_segments']):
                target_segs = [x.strip() for x in str(row['target_segments']).split(';')]

            # City tiers
            tiers = [int(x) for x in str(row['available_city_tiers']).split(';')]

            item = {
                'product_id': pid,
                'category': str(row['category']).strip(),
                'product_name': str(row['product_name']).strip(),
                'description': str(row['description']).strip(),
                'unit': str(row['unit']).strip(),
                'price_min_inr_per_month': int(row['price_min_inr_per_month']),
                'price_max_inr_per_month': int(row['price_max_inr_per_month']),
                'one_time_setup_inr': int(row['one_time_setup_inr']),
                'min_contract_months': int(row['min_contract_months']),
                'available_city_tiers': tiers,
                'min_employees': int(row['min_employees']) if pd.notna(row['min_employees']) else 1,
                'min_sites': int(row['min_sites']) if pd.notna(row['min_sites']) else 1,
                'requires_gstin': str(row['requires_gstin']).strip().upper() == 'Y',
                'requires_one_of': req_one,
                'typical_install_days': int(row['typical_install_days']),
                'target_segments': target_segs
            }

            self.products[pid] = item
            self.category_index.setdefault(item['category'], []).append(pid)
            for seg in target_segs:
                self.segment_index.setdefault(seg, []).append(pid)

    def get_all(self) -> List[dict]:
        return list(self.products.values())

    def get_product(self, product_id: str) -> Optional[dict]:
        return self.products.get(product_id.strip().upper())

    def get_by_category(self, category: str) -> List[dict]:
        pids = self.category_index.get(category, [])
        return [self.products[pid] for pid in pids]

    def get_by_segment(self, segment_code: str) -> List[dict]:
        pids = self.segment_index.get(segment_code, [])
        return [self.products[pid] for pid in pids]

    def validate_selection(
        self, 
        selected_product_ids: List[str], 
        city_tier: int = 1, 
        employees: int = 1, 
        sites: int = 1, 
        has_gstin: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validates product selection against catalogue constraints.
        Returns: (is_valid, list_of_errors, list_of_suggested_fixes)
        """
        errors = []
        suggestions = []
        selected_set: Set[str] = {pid.strip().upper() for pid in selected_product_ids}

        for pid in selected_set:
            p = self.products.get(pid)
            if not p:
                errors.append(f"Product '{pid}' does not exist in the active catalogue.")
                continue

            # Rule 1: GSTIN Requirement
            if p['requires_gstin'] and not has_gstin:
                errors.append(f"'{p['product_name']}' ({pid}) requires an active GST registration.")
                # Suggest non-GST alternative if connectivity
                if pid in ['P03', 'P05', 'P06']:
                    suggestions.append(f"Replace '{p['product_name']}' with Biz Fibre 100 (P01) or Biz 5G AirFiber (P04) which do not require GST.")
                elif pid == 'P10':
                    suggestions.append("Managed SD-WAN requires GST. Consider unmanaged multi-site fibre failover (P09).")

            # Rule 2: City Tier Availability
            if city_tier not in p['available_city_tiers']:
                errors.append(f"'{p['product_name']}' ({pid}) is only available in City Tier {p['available_city_tiers']} (Customer is in Tier {city_tier}).")
                if pid == 'P03' and city_tier == 2:
                    suggestions.append("Biz Fibre 1G is Tier 1 only. Select Biz Fibre 300 (P02) for Tier 2 locations.")

            # Rule 3: Minimum Employee Scale
            if employees < p['min_employees']:
                errors.append(f"'{p['product_name']}' ({pid}) requires a minimum of {p['min_employees']} employees (business has {employees}).")

            # Rule 4: Minimum Operating Sites
            if sites < p['min_sites']:
                errors.append(f"'{p['product_name']}' ({pid}) requires at least {p['min_sites']} operating sites (business has {sites}).")

            # Rule 5: Directed Graph Dependencies (requires_one_of)
            if p['requires_one_of']:
                has_prerequisite = any(dep in selected_set for dep in p['requires_one_of'])
                if not has_prerequisite:
                    dep_names = [self.products[d]['product_name'] for d in p['requires_one_of'] if d in self.products]
                    errors.append(f"'{p['product_name']}' ({pid}) requires at least one base connection: {', '.join(dep_names)}.")
                    suggestions.append(f"Add Biz Fibre 100 ({p['requires_one_of'][0]}) to satisfy base connection requirement for '{p['product_name']}'.")

        is_valid = len(errors) == 0
        return (is_valid, errors, suggestions)

    def calculate_bundle_pricing(
        self, 
        items: List[dict],
        price_tier: str = "min"
    ) -> dict:
        """
        Calculates exact bundle pricing, contract parameters, and savings.
        items: [{'product_id': 'P01', 'quantity': 1}, ...]
        price_tier: 'min' (baseline offer) or 'max' (unconstrained)
        """
        monthly_total = 0
        setup_total = 0
        max_contract = 1
        max_install_days = 1
        item_breakdown = []

        for it in items:
            pid = it['product_id'].strip().upper()
            qty = max(1, int(it.get('quantity', 1)))
            p = self.products.get(pid)
            if not p:
                continue

            unit_price = p['price_min_inr_per_month'] if price_tier == 'min' else p['price_max_inr_per_month']
            total_monthly_item = unit_price * qty
            item_setup = p['one_time_setup_inr']

            monthly_total += total_monthly_item
            setup_total += item_setup
            max_contract = max(max_contract, p['min_contract_months'])
            max_install_days = max(max_install_days, p['typical_install_days'])

            item_breakdown.append({
                'product_id': pid,
                'product_name': p['product_name'],
                'category': p['category'],
                'unit': p['unit'],
                'quantity': qty,
                'unit_price_inr': unit_price,
                'total_monthly_inr': total_monthly_item,
                'setup_fee_inr': item_setup,
                'install_days': p['typical_install_days'],
                'contract_months': p['min_contract_months']
            })

        # Econometric Savings Model vs Unorganized Fragmented Vendors
        # Fragmented market benchmark: Multiple individual bills carry ~35-45% aggregate markup
        unorganized_monthly = int(monthly_total * 1.40)
        unorganized_setup = setup_total + (1500 * len(item_breakdown)) # Fragmented local installers charge individual installation fees
        
        monthly_savings = unorganized_monthly - monthly_total
        annual_savings = monthly_savings * 12
        first_year_total_savings = annual_savings + max(0, unorganized_setup - setup_total)

        return {
            'item_count': len(item_breakdown),
            'monthly_recurring_total_inr': monthly_total,
            'monthly_total_inr': monthly_total,
            'one_time_setup_total_inr': setup_total,
            'setup_total_inr': setup_total,
            'effective_first_month_cost_inr': monthly_total + setup_total,
            'contract_lock_months': max_contract,
            'estimated_install_sla_days': max_install_days,
            'items': item_breakdown,
            'vendor_savings_benchmark': {
                'unorganized_market_monthly_inr': unorganized_monthly,
                'monthly_savings_inr': monthly_savings,
                'annual_savings_inr': annual_savings,
                'first_year_total_savings_inr': first_year_total_savings,
                'savings_percentage': 28.5
            }
        }
