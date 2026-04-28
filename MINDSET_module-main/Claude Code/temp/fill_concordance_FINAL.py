import pandas as pd
import numpy as np

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude.xlsx"

# Read the file
df = pd.read_excel(file_path, header=None)  # Read without header

print("="*80)
print("FILLING GLORIA-EORA26 CONCORDANCE MATRIX")
print("="*80)

# Get sector names from row 0 (columns 1-25)
eora_sectors = []
for i in range(1, 26):
    sector_name = df.iloc[0, i]
    eora_sectors.append(sector_name)

print(f"\n{len(eora_sectors)} Eora26 sectors identified")

# Get GLORIA product names (rows 1-120, column 0)
gloria_products = []
for i in range(1, 121):
    product_name = df.iloc[i, 0]
    gloria_products.append(product_name)

print(f"{len(gloria_products)} GLORIA products identified")

print("\nCreating concordance mapping...")

def map_product_to_sectors(product_name):
    """Map a GLORIA product name to Eora26 sector(s)."""
    product_lower = product_name.lower()
    sectors = []

    # 1. Agriculture
    ag_keywords = ['growing', 'raising', 'seeds', 'plant propagation', 'services to agriculture',
                   'cattle', 'sheep', 'goats', 'swine', 'pigs', 'poultry', 'animals']
    if any(kw in product_lower for kw in ag_keywords):
        if 'forestry' not in product_lower and 'fishing' not in product_lower:
            sectors.append(1)

    # 2. Fishing
    fishing_keywords = ['fishing', 'crustaceans', 'molluscs', 'aquaculture']
    if any(kw in product_lower for kw in fishing_keywords):
        sectors.append(2)

    # 3. Mining and quarrying
    mining_keywords = ['coal', 'lignite', 'peat', 'petroleum extraction', 'gas extraction',
                      'ores', 'uranium', 'aluminium', 'copper', 'nickel', 'lead', 'zinc',
                      'gold', 'diamonds', 'salt', 'stone', 'gravel', 'sand', 'clay',
                      'quarrying', 'mining']
    if any(kw in product_lower for kw in mining_keywords):
        sectors.append(3)

    # 4. Food and beverages
    food_keywords = ['meat', 'fish products', 'dairy', 'grain mill', 'starch', 'bakery',
                    'sugar', 'cocoa', 'chocolate', 'pasta', 'coffee', 'tea', 'condiments',
                    'prepared meals', 'pet food', 'beverages', 'wines', 'spirits',
                    'beer', 'soft drinks', 'mineral waters', 'tobacco products']
    if any(kw in product_lower for kw in food_keywords):
        sectors.append(4)

    # 5. Textiles and wearing apparel
    textile_keywords = ['textiles', 'wearing apparel', 'leather', 'footwear', 'yarn',
                       'fabrics', 'carpets', 'cordage', 'rope', 'knitted', 'fur']
    if any(kw in product_lower for kw in textile_keywords):
        sectors.append(5)

    # 6. Wood and paper
    wood_keywords = ['forestry', 'logging', 'wood', 'sawmilling', 'veneer', 'plywood',
                    'joinery', 'carpentry', 'containers of wood', 'cork', 'straw',
                    'pulp', 'paper', 'paperboard', 'printing', 'reproduction of recorded media']
    if any(kw in product_lower for kw in wood_keywords):
        sectors.append(6)

    # 7. Petroleum, chemical and non-metallic mineral products
    chemical_keywords = ['coke', 'refined petroleum', 'chemicals', 'fertilizers', 'pesticides',
                        'plastics', 'synthetic rubber', 'paints', 'pharmaceuticals',
                        'soap', 'detergents', 'cosmetics', 'explosives', 'glue', 'essential oils',
                        'photographic', 'fibres', 'glass', 'ceramic', 'tiles', 'bricks',
                        'cement', 'lime', 'plaster', 'concrete', 'stone products', 'abrasive']
    if any(kw in product_lower for kw in chemical_keywords):
        sectors.append(7)

    # 8. Metal products
    metal_keywords = ['iron', 'steel', 'aluminium products', 'precious metals', 'copper products',
                     'basic metals', 'casting', 'metal products', 'weapons', 'ammunition',
                     'cutlery', 'tools', 'locks', 'hinges']
    if any(kw in product_lower for kw in metal_keywords):
        if 'ores' not in product_lower:
            sectors.append(8)

    # 9. Electrical and machinery
    electrical_keywords = ['engines', 'turbines', 'pumps', 'compressors', 'bearings', 'gears',
                          'ovens', 'furnaces', 'lifting equipment', 'machinery', 'agricultural machinery',
                          'metal-forming machinery', 'machine tools', 'weapons systems',
                          'computer', 'electronic', 'optical', 'electrical equipment',
                          'electric motors', 'batteries', 'cables', 'lighting', 'appliances',
                          'television', 'radio', 'telephone', 'measuring instruments', 'watches', 'clocks']
    if any(kw in product_lower for kw in electrical_keywords):
        sectors.append(9)

    # 10. Transport equipment
    transport_keywords = ['motor vehicles', 'automobiles', 'trucks', 'buses', 'trailers',
                         'parts and accessories for motor vehicles', 'ships', 'boats',
                         'railway locomotives', 'rolling stock', 'aircraft', 'spacecraft',
                         'military vehicles', 'motorcycles', 'bicycles']
    if any(kw in product_lower for kw in transport_keywords):
        sectors.append(10)

    # 11. Other manufacturing
    other_manuf_keywords = ['furniture', 'jewellery', 'musical instruments', 'sports goods',
                           'games', 'toys', 'medical instruments', 'dental instruments',
                           'surgical instruments', 'dentures', 'wheelchairs', 'brooms', 'brushes']
    if any(kw in product_lower for kw in other_manuf_keywords):
        sectors.append(11)

    # 12. Recycling
    recycling_keywords = ['recycling', 'waste collection', 'waste treatment', 'recovery of materials']
    if any(kw in product_lower for kw in recycling_keywords):
        sectors.append(12)

    # 13. Electricity, gas and water
    utility_keywords = ['electricity', 'gas', 'steam', 'air conditioning', 'water collection',
                       'water treatment', 'water distribution', 'sewerage']
    if any(kw in product_lower for kw in utility_keywords):
        sectors.append(13)

    # 14. Construction
    construction_keywords = ['construction of buildings', 'civil engineering', 'construction of roads',
                            'railways', 'utility projects', 'specialized construction', 'demolition',
                            'site preparation', 'electrical installation', 'plumbing', 'painting',
                            'glazing', 'plastering', 'finishing', 'roofing', 'scaffold']
    if any(kw in product_lower for kw in construction_keywords):
        sectors.append(14)

    # 15. Maintenance and repair
    maintenance_keywords = ['repair', 'maintenance', 'installation']
    if any(kw in product_lower for kw in maintenance_keywords):
        if not any(kw in product_lower for kw in construction_keywords):
            sectors.append(15)

    # 16. Wholesale trade
    wholesale_keywords = ['wholesale trade']
    if any(kw in product_lower for kw in wholesale_keywords):
        sectors.append(16)

    # 17. Retail trade
    retail_keywords = ['retail trade', 'retail sale']
    if any(kw in product_lower for kw in retail_keywords):
        sectors.append(17)

    # 18. Hotels and restaurants
    hospitality_keywords = ['accommodation', 'hotels', 'camping', 'food service', 'restaurants',
                           'event catering', 'drinking places', 'bars']
    if any(kw in product_lower for kw in hospitality_keywords):
        sectors.append(18)

    # 19. Transport
    transport_service_keywords = ['land transport', 'rail transport', 'road transport',
                                  'water transport', 'air transport', 'pipeline transport',
                                  'warehousing', 'storage', 'cargo handling', 'travel agency',
                                  'tour operator']
    if any(kw in product_lower for kw in transport_service_keywords):
        sectors.append(19)

    # 20. Post and telecommunications
    telecom_keywords = ['postal', 'courier', 'telecommunications', 'broadcasting']
    if any(kw in product_lower for kw in telecom_keywords):
        sectors.append(20)

    # 21. Financial intermediation and business activities
    finance_keywords = ['financial', 'insurance', 'banking', 'investment', 'pension funding',
                       'securities', 'real estate', 'legal', 'accounting', 'management consulting',
                       'architectural', 'engineering', 'technical testing', 'research and development',
                       'advertising', 'market research', 'head offices', 'employment activities',
                       'security services', 'cleaning', 'landscaping', 'office administration']
    if any(kw in product_lower for kw in finance_keywords):
        sectors.append(21)

    # 22. Public administration
    admin_keywords = ['public administration', 'defence', 'compulsory social security']
    if any(kw in product_lower for kw in admin_keywords):
        sectors.append(22)

    # 23. Education, health and other services
    social_keywords = ['education', 'human health', 'residential care', 'social work',
                      'creative', 'arts', 'entertainment', 'libraries', 'archives', 'museums',
                      'gambling', 'betting', 'sports', 'amusement', 'recreation',
                      'membership organizations']
    if any(kw in product_lower for kw in social_keywords):
        sectors.append(23)

    # 24. Private households
    household_keywords = ['private households', 'household as employers', 'domestic personnel']
    if any(kw in product_lower for kw in household_keywords):
        sectors.append(24)

    # 25. Other (fallback)
    if len(sectors) == 0:
        sectors.append(25)

    return sectors

# Create concordance matrix
concordance_matrix = np.zeros((120, 25), dtype=int)
mapping_log = []

for i, product in enumerate(gloria_products):
    sector_indices = map_product_to_sectors(product)
    for sector_idx in sector_indices:
        concordance_matrix[i, sector_idx - 1] = 1

    sector_names = [eora_sectors[idx-1] for idx in sector_indices]
    mapping_log.append({
        'Product': product,
        'Mapped_to': ', '.join(sector_names)
    })

    if (i+1) % 20 == 0:
        print(f"  Processed {i+1}/120 products...")

print(f"\nCompleted mapping all 120 products")

# Fill the dataframe
print("Filling the matrix with 1s and 0s...")
for i in range(120):
    for j in range(25):
        df.iloc[i+1, j+1] = concordance_matrix[i, j]

# Save
output_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude - FILLED.xlsx"
print(f"\nSaving to: {output_path}")
df.to_excel(output_path, index=False, header=False)
print("SUCCESS: Saved filled concordance matrix")

# Save mapping log
mapping_df = pd.DataFrame(mapping_log)
log_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Mapping_Log.xlsx"
mapping_df.to_excel(log_path, index=False)
print(f"SUCCESS: Saved mapping log")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
for j, sector in enumerate(eora_sectors):
    count = concordance_matrix[:, j].sum()
    print(f"  {sector}: {count} products")

print(f"\nTotal: {concordance_matrix.sum()} mappings")

print("\nFirst 15 products:")
for i in range(15):
    product = gloria_products[i]
    sectors_mapped = [eora_sectors[j] for j in range(25) if concordance_matrix[i, j] == 1]
    print(f"  {product} -> {', '.join(sectors_mapped)}")

print("\n" + "="*80)
print("DONE!")
print("="*80)
