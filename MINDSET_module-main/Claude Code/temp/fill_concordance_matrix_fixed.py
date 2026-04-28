import pandas as pd
import numpy as np

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude.xlsx"

# Read the file
df = pd.read_excel(file_path, header=0)

print("="*80)
print("FILLING GLORIA-EORA26 CONCORDANCE MATRIX")
print("="*80)

# Get sector names from row 0 (columns 1-25)
eora_sectors = []
for i in range(1, 26):
    sector_name = df.iloc[0, i]
    eora_sectors.append(sector_name)

print(f"\n{len(eora_sectors)} Eora26 sectors identified:")
for i, sector in enumerate(eora_sectors, 1):
    print(f"  {i}. {sector}")

# Get GLORIA product names (rows 1-120, column 0)
gloria_products = []
for i in range(1, 121):
    product_name = df.iloc[i, 0]
    gloria_products.append(product_name)

print(f"\n{len(gloria_products)} GLORIA products identified")
print("First 10:", gloria_products[:10])

print("\n" + "="*80)
print("CREATING CONCORDANCE MAPPING")
print("="*80)

# Define mapping rules: GLORIA product keywords → Eora sector index
# This is a comprehensive mapping based on product names

def map_product_to_sectors(product_name):
    """
    Map a GLORIA product name to Eora26 sector(s).
    Returns a list of sector indices (1-25) that the product belongs to.
    """
    product_lower = product_name.lower()
    sectors = []

    # 1. Agriculture
    ag_keywords = ['growing', 'raising', 'seeds', 'plant propagation', 'services to agriculture',
                   'cattle', 'sheep', 'goats', 'swine', 'pigs', 'poultry', 'animals']
    if any(kw in product_lower for kw in ag_keywords):
        if 'forestry' not in product_lower and 'fishing' not in product_lower:
            sectors.append(1)  # Agriculture

    # 2. Fishing
    fishing_keywords = ['fishing', 'crustaceans', 'molluscs', 'aquaculture']
    if any(kw in product_lower for kw in fishing_keywords):
        sectors.append(2)  # Fishing

    # 3. Mining and quarrying
    mining_keywords = ['coal', 'lignite', 'peat', 'petroleum extraction', 'gas extraction',
                      'ores', 'uranium', 'aluminium', 'copper', 'nickel', 'lead', 'zinc',
                      'gold', 'diamonds', 'salt', 'stone', 'gravel', 'sand', 'clay',
                      'quarrying', 'mining']
    if any(kw in product_lower for kw in mining_keywords):
        sectors.append(3)  # Mining and quarrying

    # 4. Food and beverages
    food_keywords = ['meat', 'fish products', 'dairy', 'grain mill', 'starch', 'bakery',
                    'sugar', 'cocoa', 'chocolate', 'pasta', 'coffee', 'tea', 'condiments',
                    'prepared meals', 'pet food', 'beverages', 'wines', 'spirits',
                    'beer', 'soft drinks', 'mineral waters', 'tobacco products']
    if any(kw in product_lower for kw in food_keywords):
        sectors.append(4)  # Food and beverages

    # 5. Textiles and wearing apparel
    textile_keywords = ['textiles', 'wearing apparel', 'leather', 'footwear', 'yarn',
                       'fabrics', 'carpets', 'cordage', 'rope', 'knitted', 'fur']
    if any(kw in product_lower for kw in textile_keywords):
        sectors.append(5)  # Textiles and wearing apparel

    # 6. Wood and paper
    wood_keywords = ['forestry', 'logging', 'wood', 'sawmilling', 'veneer', 'plywood',
                    'joinery', 'carpentry', 'containers of wood', 'cork', 'straw',
                    'pulp', 'paper', 'paperboard', 'printing', 'reproduction of recorded media']
    if any(kw in product_lower for kw in wood_keywords):
        sectors.append(6)  # Wood and paper

    # 7. Petroleum, chemical and non-metallic mineral products
    chemical_keywords = ['coke', 'refined petroleum', 'chemicals', 'fertilizers', 'pesticides',
                        'plastics', 'synthetic rubber', 'paints', 'pharmaceuticals',
                        'soap', 'detergents', 'cosmetics', 'explosives', 'glue', 'essential oils',
                        'photographic', 'fibres', 'glass', 'ceramic', 'tiles', 'bricks',
                        'cement', 'lime', 'plaster', 'concrete', 'stone products', 'abrasive']
    if any(kw in product_lower for kw in chemical_keywords):
        sectors.append(7)  # Petroleum, chemical and non-metallic mineral products

    # 8. Metal products
    metal_keywords = ['iron', 'steel', 'aluminium products', 'precious metals', 'copper products',
                     'basic metals', 'casting', 'metal products', 'weapons', 'ammunition',
                     'cutlery', 'tools', 'locks', 'hinges']
    if any(kw in product_lower for kw in metal_keywords):
        if 'ores' not in product_lower:  # Ores go to mining, not metal products
            sectors.append(8)  # Metal products

    # 9. Electrical and machinery
    electrical_keywords = ['engines', 'turbines', 'pumps', 'compressors', 'bearings', 'gears',
                          'ovens', 'furnaces', 'lifting equipment', 'machinery', 'agricultural machinery',
                          'metal-forming machinery', 'machine tools', 'weapons systems',
                          'computer', 'electronic', 'optical', 'electrical equipment',
                          'electric motors', 'batteries', 'cables', 'lighting', 'appliances',
                          'television', 'radio', 'telephone', 'measuring instruments', 'watches', 'clocks']
    if any(kw in product_lower for kw in electrical_keywords):
        sectors.append(9)  # Electrical and machinery

    # 10. Transport equipment
    transport_keywords = ['motor vehicles', 'automobiles', 'trucks', 'buses', 'trailers',
                         'parts and accessories for motor vehicles', 'ships', 'boats',
                         'railway locomotives', 'rolling stock', 'aircraft', 'spacecraft',
                         'military vehicles', 'motorcycles', 'bicycles']
    if any(kw in product_lower for kw in transport_keywords):
        sectors.append(10)  # Transport equipment

    # 11. Other manufacturing
    other_manuf_keywords = ['furniture', 'jewellery', 'musical instruments', 'sports goods',
                           'games', 'toys', 'medical instruments', 'dental instruments',
                           'surgical instruments', 'dentures', 'wheelchairs', 'brooms', 'brushes']
    if any(kw in product_lower for kw in other_manuf_keywords):
        sectors.append(11)  # Other manufacturing

    # 12. Recycling
    recycling_keywords = ['recycling', 'waste collection', 'waste treatment', 'recovery of materials']
    if any(kw in product_lower for kw in recycling_keywords):
        sectors.append(12)  # Recycling

    # 13. Electricity, gas and water
    utility_keywords = ['electricity', 'gas', 'steam', 'air conditioning', 'water collection',
                       'water treatment', 'water distribution', 'sewerage']
    if any(kw in product_lower for kw in utility_keywords):
        sectors.append(13)  # Electricity, gas and water

    # 14. Construction
    construction_keywords = ['construction of buildings', 'civil engineering', 'construction of roads',
                            'railways', 'utility projects', 'specialized construction', 'demolition',
                            'site preparation', 'electrical installation', 'plumbing', 'painting',
                            'glazing', 'plastering', 'finishing', 'roofing', 'scaffold']
    if any(kw in product_lower for kw in construction_keywords):
        sectors.append(14)  # Construction

    # 15. Maintenance and repair
    maintenance_keywords = ['repair', 'maintenance', 'installation']
    if any(kw in product_lower for kw in maintenance_keywords):
        # Avoid double-counting with Construction
        if not any(kw in product_lower for kw in construction_keywords):
            sectors.append(15)  # Maintenance and repair

    # 16. Wholesale trade
    wholesale_keywords = ['wholesale trade']
    if any(kw in product_lower for kw in wholesale_keywords):
        sectors.append(16)  # Wholesale trade

    # 17. Retail trade
    retail_keywords = ['retail trade', 'retail sale']
    if any(kw in product_lower for kw in retail_keywords):
        sectors.append(17)  # Retail trade

    # 18. Hotels and restaurants
    hospitality_keywords = ['accommodation', 'hotels', 'camping', 'food service', 'restaurants',
                           'event catering', 'drinking places', 'bars']
    if any(kw in product_lower for kw in hospitality_keywords):
        sectors.append(18)  # Hotels and restaurants

    # 19. Transport
    transport_service_keywords = ['land transport', 'rail transport', 'road transport',
                                  'water transport', 'air transport', 'pipeline transport',
                                  'warehousing', 'storage', 'cargo handling', 'travel agency',
                                  'tour operator']
    if any(kw in product_lower for kw in transport_service_keywords):
        sectors.append(19)  # Transport

    # 20. Post and telecommunications
    telecom_keywords = ['postal', 'courier', 'telecommunications', 'broadcasting']
    if any(kw in product_lower for kw in telecom_keywords):
        sectors.append(20)  # Post and telecommunications

    # 21. Financial intermediation and business activities
    finance_keywords = ['financial', 'insurance', 'banking', 'investment', 'pension funding',
                       'securities', 'real estate', 'legal', 'accounting', 'management consulting',
                       'architectural', 'engineering', 'technical testing', 'research and development',
                       'advertising', 'market research', 'head offices', 'employment activities',
                       'security services', 'cleaning', 'landscaping', 'office administration']
    if any(kw in product_lower for kw in finance_keywords):
        sectors.append(21)  # Financial intermediation and business activities

    # 22. Public administration
    admin_keywords = ['public administration', 'defence', 'compulsory social security']
    if any(kw in product_lower for kw in admin_keywords):
        sectors.append(22)  # Public administration

    # 23. Education, health and other services
    social_keywords = ['education', 'human health', 'residential care', 'social work',
                      'creative', 'arts', 'entertainment', 'libraries', 'archives', 'museums',
                      'gambling', 'betting', 'sports', 'amusement', 'recreation',
                      'membership organizations']
    if any(kw in product_lower for kw in social_keywords):
        sectors.append(23)  # Education, health and other services

    # 24. Private households
    household_keywords = ['private households', 'household as employers', 'domestic personnel']
    if any(kw in product_lower for kw in household_keywords):
        sectors.append(24)  # Private households

    # 25. Other (fallback for anything not matched)
    if len(sectors) == 0:
        sectors.append(25)  # Other

    return sectors


# Create the concordance matrix (120 products × 25 sectors)
concordance_matrix = np.zeros((120, 25), dtype=int)

print("\nMapping products to sectors...")
mapping_log = []

for i, product in enumerate(gloria_products):
    sector_indices = map_product_to_sectors(product)
    for sector_idx in sector_indices:
        concordance_matrix[i, sector_idx - 1] = 1  # -1 because indices are 1-based

    # Log the mapping
    sector_names = [eora_sectors[idx-1] for idx in sector_indices]
    mapping_log.append({
        'Product': product,
        'Mapped_to': ', '.join(sector_names)
    })

    if (i+1) % 20 == 0:
        print(f"  Processed {i+1}/120 products...")

print(f"\nSUCCESS: Completed mapping all 120 products")

# Fill the dataframe with the concordance matrix
for i in range(120):
    for j in range(25):
        df.iloc[i+1, j+1] = concordance_matrix[i, j]

# Save the filled matrix
output_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude - FILLED.xlsx"
df.to_excel(output_path, index=False, header=False)

print(f"\nSUCCESS: Saved filled concordance matrix to:")
print(f"  {output_path}")

# Save mapping log for verification
mapping_df = pd.DataFrame(mapping_log)
log_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Mapping_Log.xlsx"
mapping_df.to_excel(log_path, index=False)

print(f"\nSUCCESS: Saved mapping log to:")
print(f"  {log_path}")

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

# Summary statistics
for j, sector in enumerate(eora_sectors):
    count = concordance_matrix[:, j].sum()
    print(f"  {sector}: {count} products")

print(f"\nTotal mappings: {concordance_matrix.sum()} (some products may map to multiple sectors)")

print("\n" + "="*80)
print("SAMPLE VERIFICATION (first 10 products)")
print("="*80)
for i in range(10):
    product = gloria_products[i]
    sectors = [eora_sectors[j] for j in range(25) if concordance_matrix[i, j] == 1]
    print(f"  {product[:50]:50} → {', '.join(sectors)}")

print("\n" + "="*80)
print("DONE!")
print("="*80)
