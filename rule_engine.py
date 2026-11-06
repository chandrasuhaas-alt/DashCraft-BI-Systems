"""
DashCraft BI — Rule Engine
Infers column types and applies design rules to any dataframe.
"""

import inspect
import pandas as pd


def infer_col_type(series: pd.Series) -> str:
    """Infer whether a column is numerical, temporal, or categorical."""
    if pd.api.types.is_numeric_dtype(series):
        return "numerical"
    # Try datetime parse on a small sample
    try:
        parsed = pd.to_datetime(series.dropna().head(20), infer_datetime_format=True, errors="raise")
        if parsed.notna().sum() >= len(series.dropna().head(20)) * 0.8:
            return "temporal"
    except Exception:
        pass
    return "categorical"


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Return a full column profile."""
    profile = {}
    for col in df.columns:
        ctype = infer_col_type(df[col])
        entry = {
            "type":     ctype,
            "n_unique": int(df[col].nunique()),
            "null_pct": round(df[col].isnull().mean() * 100, 1),
            "sample":   df[col].dropna().head(3).tolist(),
        }
        if ctype == "numerical":
            entry.update({
                "mean":   round(float(df[col].mean()),   2),
                "median": round(float(df[col].median()), 2),
                "min":    round(float(df[col].min()),    2),
                "max":    round(float(df[col].max()),    2),
                "std":    round(float(df[col].std()),    2),
            })
        profile[col] = entry
    return profile


RULES = [
    {
        "id":          "R1",
        "name":        "Temporal Trend — Area Chart",
        "condition":   lambda num, cat, tmp: len(tmp) > 0 and len(num) > 0,
        "chart":       "area",
        "position":    "Top — full width",
        "size":        "large",
        "confidence":  0.94,
        "description": "When time is on the X-axis, tell the story with an area trend chart.",
        "priority":    1,
        "build":       lambda num, cat, tmp: {"x": tmp[0], "y": num[0], "y2": num[1] if len(num) > 1 else None},
    },
    {
        "id":          "R2",
        "name":        "Executive KPI Summary Cards",
        "condition":   lambda num, cat, tmp, role="executive": role == "executive" and len(num) >= 1,
        "chart":       "kpi",
        "position":    "Header row",
        "size":        "small",
        "confidence":  0.96,
        "description": "Executives are busy. Give them the big numbers up top.",
        "priority":    0,
        "build":       lambda num, cat, tmp: {"cols": num[:4]},
    },
    {
        "id":          "R3",
        "name":        "Categorical Comparison — Bar Chart",
        "condition":   lambda num, cat, tmp: len(cat) > 0 and len(num) >= 1,
        "chart":       "bar",
        "position":    "Left column",
        "size":        "medium",
        "confidence":  0.88,
        "description": "Compare categories side by side. Like twins — they belong together.",
        "priority":    2,
        "build":       lambda num, cat, tmp: {"x": cat[0], "y": num[0], "y2": num[1] if len(num) > 1 else None},
    },
    {
        "id":          "R4",
        "name":        "Distribution — Donut Chart",
        "condition":   lambda num, cat, tmp: len(cat) > 0 and len(num) >= 1,
        "chart":       "pie",
        "position":    "Right column",
        "size":        "medium",
        "confidence":  0.82,
        "description": "Categorical breakdown with a single metric. We stand our ground on donut charts.",
        "priority":    3,
        "build":       lambda num, cat, tmp: {"names": cat[0], "values": num[0]},
    },
    {
        "id":          "R5",
        "name":        "Correlation — Scatter Plot (Analyst)",
        "condition":   lambda num, cat, tmp, role="analyst": role == "analyst" and len(num) >= 2,
        "chart":       "scatter",
        "position":    "Bottom left",
        "size":        "medium",
        "confidence":  0.79,
        "description": "Two numerical fields? Find the relationship with a scatter plot and trendline.",
        "priority":    4,
        "build":       lambda num, cat, tmp: {"x": num[0], "y": num[1]},
    },
    {
        "id":          "R6",
        "name":        "Secondary Metric — Line Chart",
        "condition":   lambda num, cat, tmp: len(num) >= 2,
        "chart":       "line",
        "position":    "Bottom — full width",
        "size":        "medium",
        "confidence":  0.85,
        "description": "Your second most important metric still deserves a chart of its own.",
        "priority":    5,
        "build":       lambda num, cat, tmp: {"x": cat[0] if cat else num[0], "y": num[-1]},
    },
]


def apply_rules(df: pd.DataFrame, profile: dict, role: str) -> list:
    """Apply design rules and return a list of chart recommendations."""
    num_cols = [c for c, p in profile.items() if p["type"] == "numerical"]
    cat_cols = [c for c, p in profile.items() if p["type"] == "categorical"]
    tmp_cols = [c for c, p in profile.items() if p["type"] == "temporal"]

    recommendations = []
    for rule in sorted(RULES, key=lambda r: r["priority"]):
        try:
            if rule["id"] == "R2" and role != "executive":
                continue
            if rule["id"] == "R5" and role != "analyst":
                continue

            cond = rule["condition"]
            sig  = inspect.signature(cond)
            applies = (
                cond(num_cols, cat_cols, tmp_cols, role=role)
                if "role" in sig.parameters
                else cond(num_cols, cat_cols, tmp_cols)
            )
            if applies:
                cfg = rule["build"](num_cols, cat_cols, tmp_cols)
                recommendations.append({
                    **{k: v for k, v in rule.items() if k not in ("condition", "build")},
                    "config": cfg,
                })
        except Exception:
            continue

    return recommendations
