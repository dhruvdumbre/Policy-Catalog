import pandas as pd
from database import get_all_policies

COLUMNS = [
    "policy_type_id",
    "name",
    "category",
    "min_premium",
    "max_premium",
    "coverage_amount",
]

def get_analytics():
    records = get_all_policies()
    df = pd.DataFrame(records, columns = COLUMNS)
    
    if df.empty:
        return {
            "summary": {
                "total_policies": 0,
                "total_categories": 0,
                "average_min_premium": 0,
                "average_max_premium": 0,
                "total_coverage": 0,
                "average_coverage": 0,
            },
            "categories": [],
            "top_coverage": [],
        }
        
    numeric_columns = [
        "min_premium",
        "max_premium",
        "coverage_amount",
    ]
    
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors = "coerce")
        
    category_stats = (
        df.groupby("category", dropna=False)
        .agg(
            policy_count =("policy_type_id", "count"),
            average_min_premium = ("min_premium", "mean"),
            average_max_premium = ("max_premium", "mean"),
            average_coverage = ("coverage_amount", "mean"),
            total_coverage = ("coverage_amount", "sum"),
        )
        .reset_index()
    )
    
    top_coverage = (
        df.nlargest(5, "coverage_amount")[
            ["policy_type_id", "name", "category", "coverage_amount"]
        ]
    )
    
    summary = {
        "total_policies": int(len(df)),
        "total_categories": int(df["category"].nunique()),
        "average_min_premium": float(df["min_premium"].mean()),
        "average_max_premium": float(df["max_premium"].mean()),
        "total_coverage": float(df["coverage_amount"].sum()),
        "average_coverage": float(df["coverage_amount"].mean()),
    }
    
    return {
        "summary": summary,
        "categories": category_stats.to_dict(orient="records"),
        "top_coverage": top_coverage.to_dict(orient="records"),
    }