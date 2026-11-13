import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, date, timedelta

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUTPUT_FOLDER = "daily_sales_data"   # folder where CSVs will be dropped
SIMULATE_DATE = date.today()         # change to any date to backfill
ROWS = random.randint(400, 600)      # realistic daily variance
# ──────────────────────────────────────────────────────────────────────────────

random.seed(int(SIMULATE_DATE.strftime("%Y%m%d")))  # same date = same data (reproducible)
np.random.seed(int(SIMULATE_DATE.strftime("%Y%m%d")))

# ─── REFERENCE DATA ───────────────────────────────────────────────────────────

REGIONS = {
    "North":   ["Delhi", "Chandigarh", "Lucknow", "Jaipur"],
    "South":   ["Bangalore", "Chennai", "Hyderabad", "Kochi"],
    "East":    ["Kolkata", "Bhubaneswar", "Patna", "Guwahati"],
    "West":    ["Mumbai", "Pune", "Ahmedabad", "Surat"],
    "Central": ["Nagpur", "Bhopal", "Indore", "Raipur"],
}

SALESPERSONS = [
    "Arjun Mehta", "Priya Sharma", "Rohan Das", "Sneha Iyer",
    "Vikram Singh", "Divya Nair", "Karan Patel", "Anjali Rao",
    "Nikhil Joshi", "Pooja Verma"
]

# SKU data: category -> list of (product_name, sku_id, unit_price)
SKUS = {
    "Beverages": [
        ("Tropicana Orange 1L",  "BEV-001", 95),
        ("Maaza Mango 600ml",    "BEV-002", 40),
        ("Red Bull 250ml",       "BEV-003", 125),
        ("Bisleri Water 1L",     "BEV-004", 20),
        ("Nescafe Classic 50g",  "BEV-005", 210),
        ("Glucon-D 500g",        "BEV-006", 165),
    ],
    "Snacks": [
        ("Lays Classic 90g",         "SNK-001", 30),
        ("Kurkure Masala 90g",       "SNK-002", 30),
        ("Hide & Seek Cookies 150g", "SNK-003", 55),
        ("Good Day Biscuits 200g",   "SNK-004", 45),
        ("Haldirams Bhujia 400g",    "SNK-005", 130),
        ("Maggi Noodles 70g",        "SNK-006", 14),
    ],
    "Personal Care": [
        ("Dove Soap 100g",          "PC-001", 55),
        ("Head & Shoulders 340ml",  "PC-002", 290),
        ("Colgate Toothpaste 200g", "PC-003", 110),
        ("Nivea Lotion 200ml",      "PC-004", 220),
        ("Dettol Hand Wash 250ml",  "PC-005", 95),
        ("Gillette Mach3 Razor",    "PC-006", 350),
    ],
    "Household": [
        ("Ariel Detergent 1kg",    "HH-001", 220),
        ("Vim Dishwash Gel 500ml", "HH-002", 90),
        ("Lizol Floor Cleaner 1L", "HH-003", 175),
        ("Harpic Toilet Cleaner",  "HH-004", 140),
        ("Good Knight Refill",     "HH-005", 75),
        ("Scotch Brite Scrub Pad", "HH-006", 45),
    ],
    "Dairy": [
        ("Amul Full Cream Milk 1L",  "DAI-001", 68),
        ("Amul Butter 500g",         "DAI-002", 260),
        ("Mother Dairy Curd 400g",   "DAI-003", 50),
        ("Nestle Munch Milkshake",   "DAI-004", 30),
        ("Britannia Cheese Slice",   "DAI-005", 115),
        ("Amul Ice Cream 750ml",     "DAI-006", 195),
    ],
}

PAYMENT_METHODS = ["Cash", "Card", "UPI", "Credit"]
CHANNELS       = ["In-Store", "Distributor", "Online"]
DISCOUNTS      = [0, 0, 0, 0, 5, 5, 10, 15]   # weighted towards no discount

# ─── CUSTOMER POOL (fixed pool so repeat customers appear) ────────────────────
FIRST_NAMES = ["Amit","Priya","Rahul","Sunita","Vikram","Deepa","Raj","Meena",
                "Suresh","Kavya","Arun","Neha","Sanjay","Pooja","Ravi","Anita",
                "Manoj","Geeta","Ajay","Rekha","Sunil","Shweta","Ramesh","Usha"]
LAST_NAMES  = ["Sharma","Verma","Singh","Patel","Kumar","Rao","Nair","Joshi",
                "Mehta","Iyer","Das","Gupta","Mishra","Pillai","Reddy","Shah"]

random.seed(42)  # fixed seed for customer pool
CUSTOMER_POOL = [
    (f"CUST{str(i).zfill(4)}", f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}")
    for i in range(1, 301)
]
random.seed(int(SIMULATE_DATE.strftime("%Y%m%d")))  # restore daily seed

# ─── GENERATE ROWS ────────────────────────────────────────────────────────────

records = []
for i in range(1, ROWS + 1):
    region      = random.choice(list(REGIONS.keys()))
    city        = random.choice(REGIONS[region])
    category    = random.choice(list(SKUS.keys()))
    product     = random.choice(SKUS[category])
    cust        = random.choice(CUSTOMER_POOL)
    hour        = random.randint(9, 20)
    minute      = random.randint(0, 59)
    second      = random.randint(0, 59)
    qty_map     = {"Beverages": (5,40), "Snacks": (10,60), "Personal Care": (3,20),
                   "Household": (3,25), "Dairy": (5,35)}
    qty         = random.randint(*qty_map[category])
    discount    = random.choice(DISCOUNTS)
    return_flag = "Yes" if random.random() < 0.05 else "No"

    records.append({
        "order_id":        f"ORD-{SIMULATE_DATE.strftime('%Y%m%d')}-{str(i).zfill(4)}",
        "order_date":      SIMULATE_DATE.strftime("%Y-%m-%d"),
        "order_time":      f"{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)}",
        "customer_id":     cust[0],
        "customer_name":   cust[1],
        "region":          region,
        "city":            city,
        "salesperson":     random.choice(SALESPERSONS),
        "category":        category,
        "product_name":    product[0],
        "sku_id":          product[1],
        "quantity":        qty,
        "unit_price":      product[2],
        "discount_pct":    discount,
        "return_flag":     return_flag,
        "payment_method":  random.choice(PAYMENT_METHODS),
        "channel":         random.choice(CHANNELS),
    })

df = pd.DataFrame(records)

# ─── INJECT INTENTIONAL DIRT (so Power Query cleaning has real work to do) ────
# ~2% blank customer names
blank_idx = df.sample(frac=0.02).index
df.loc[blank_idx, "customer_name"] = ""

# ~1% duplicate order IDs (copy some rows)
dup_idx = df.sample(frac=0.01).index
df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

# ~1% negative quantity (data entry error)
neg_idx = df.sample(frac=0.01).index
df.loc[neg_idx, "quantity"] = df.loc[neg_idx, "quantity"] * -1

# ~1% missing region
missing_idx = df.sample(frac=0.01).index
df.loc[missing_idx, "region"] = ""

# shuffle so dirt isn't all at the end
df = df.sample(frac=1).reset_index(drop=True)

# ─── SAVE ─────────────────────────────────────────────────────────────────────
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
filename = os.path.join(OUTPUT_FOLDER, f"sales_{SIMULATE_DATE.strftime('%Y_%m_%d')}.csv")
df.to_csv(filename, index=False)

print(f"Generated: {filename}  |  Rows: {len(df)}  |  Date: {SIMULATE_DATE}")
