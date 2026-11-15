"""Reproducible descriptive analysis of CMS chronic-condition aggregates."""

from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "chronic-disease-data.csv"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

PAYMENT_FIELDS = [
    "Tot_Mdcr_Stdzd_Pymt_PC",
    "Tot_Mdcr_Pymt_PC",
    "Hosp_Readmsn_Rate",
    "ER_Visits_Per_1000_Benes",
]

STATES = [
    "Texas",
    "New York",
    "California",
    "Florida",
]

FIFTY_STATES_EXCLUSIONS = [
    "District of Columbia",
    "Puerto Rico",
    "Virgin Islands",
    "U.S. Virgin Islands",
]


# ============================================================
# 1. LOAD AND VALIDATE DATA
# ============================================================

def load_data():
    """Load CMS data and verify essential fields."""

    df = pd.read_csv(
        DATA,
        dtype={"Bene_Geo_Cd": "string"},
        low_memory=False,
    )

    required = {
        "Bene_Cond",
        "Bene_Geo_Lvl",
        "Bene_Geo_Desc",
        "Bene_Age_Lvl",
        "Bene_Demo_Lvl",
        "Bene_Demo_Desc",
        "Prvlnc",
        *PAYMENT_FIELDS,
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    for column in ["Prvlnc", *PAYMENT_FIELDS]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if not df["Prvlnc"].dropna().between(0, 1).all():
        raise ValueError(
            "Prevalence values must be between 0 and 1."
        )

    return df


# ============================================================
# 2. FILTER AGGREGATE DATA
# ============================================================

def aggregate_scope(df, demographic="All", age="All"):
    """Select matching demographic and age aggregations."""

    return df[
        (df["Bene_Age_Lvl"] == age)
        & (df["Bene_Demo_Lvl"] == demographic)
    ].copy()


# ============================================================
# 3. CHRONIC DISEASE PREVALENCE
# ============================================================

def prevalence_comparison(df):
    """Compare national prevalence with four selected states."""

    sub = aggregate_scope(df)

    sub = sub[
        (sub["Bene_Geo_Lvl"] == "National")
        | (
            (sub["Bene_Geo_Lvl"] == "State")
            & sub["Bene_Geo_Desc"].isin(STATES)
        )
    ]

    sub = sub[
        ["Bene_Geo_Desc", "Bene_Cond", "Prvlnc"]
    ].dropna().copy()

    sub["Prevalence_pct"] = sub["Prvlnc"] * 100

    return sub.sort_values(
        ["Bene_Cond", "Bene_Geo_Desc"]
    )


# ============================================================
# 4. MEDICARE UTILIZATION
# ============================================================

def utilization_comparison(df):
    """Extract utilization for national and selected-state data."""

    sub = aggregate_scope(df)

    sub = sub[
        (sub["Bene_Geo_Lvl"] == "National")
        | (
            (sub["Bene_Geo_Lvl"] == "State")
            & sub["Bene_Geo_Desc"].isin(STATES)
        )
    ]

    return sub[
        ["Bene_Geo_Desc", "Bene_Cond", *PAYMENT_FIELDS]
    ].sort_values(
        ["Bene_Cond", "Bene_Geo_Desc"]
    )


# ============================================================
# 5. STATE PREVALENCE EXTREMES
# ============================================================

def extrema(df, demographic="All"):
    """Find highest and lowest state prevalence values."""

    state = df[
        (df["Bene_Geo_Lvl"] == "State")
        & (df["Bene_Age_Lvl"] == "All")
        & (df["Bene_Demo_Lvl"] == demographic)
        & ~df["Bene_Geo_Desc"].isin(
            FIFTY_STATES_EXCLUSIONS
        )
    ].copy()

    nation = df[
        (df["Bene_Geo_Lvl"] == "National")
        & (df["Bene_Age_Lvl"] == "All")
        & (df["Bene_Demo_Lvl"] == demographic)
    ].copy()

    if demographic == "All":
        group = ["Bene_Cond"]
    else:
        group = ["Bene_Cond", "Bene_Demo_Desc"]

    state = state.dropna(subset=["Prvlnc"])
    nation = nation.dropna(subset=["Prvlnc"])

    if state.empty or nation.empty:
        return pd.DataFrame()

    high = state.loc[
        state.groupby(group)["Prvlnc"].idxmax(),
        group + ["Bene_Geo_Desc", "Prvlnc"],
    ].rename(
        columns={
            "Bene_Geo_Desc": "Highest_State",
            "Prvlnc": "Highest_Prev",
        }
    )

    low = state.loc[
        state.groupby(group)["Prvlnc"].idxmin(),
        group + ["Bene_Geo_Desc", "Prvlnc"],
    ].rename(
        columns={
            "Bene_Geo_Desc": "Lowest_State",
            "Prvlnc": "Lowest_Prev",
        }
    )

    national = nation[
        group + ["Prvlnc"]
    ].rename(
        columns={
            "Prvlnc": "National_Prev",
        }
    )

    result = high.merge(
        low,
        on=group,
    ).merge(
        national,
        on=group,
        how="left",
        validate="one_to_one",
    )

    for column in [
        "Highest_Prev",
        "Lowest_Prev",
        "National_Prev",
    ]:
        result[
            column.replace("Prev", "Pct")
        ] = result[column] * 100

    result["Highest_vs_National_pp"] = (
        result["Highest_Prev"]
        - result["National_Prev"]
    ) * 100

    result["Lowest_vs_National_pp"] = (
        result["Lowest_Prev"]
        - result["National_Prev"]
    ) * 100

    return result.sort_values(
        group
    ).reset_index(drop=True)


# ============================================================
# 6. NATIONAL DEMOGRAPHIC PREVALENCE
# ============================================================

def subgroup_prevalence(df, demographic):
    """Extract national prevalence by demographic subgroup."""

    sub = df[
        (df["Bene_Geo_Lvl"] == "National")
        & (df["Bene_Demo_Lvl"] == demographic)
        & (df["Bene_Age_Lvl"] == "All")
    ].copy()

    sub["Prevalence_pct"] = sub["Prvlnc"] * 100

    return sub[
        [
            "Bene_Cond",
            "Bene_Demo_Desc",
            "Prevalence_pct",
        ]
    ].dropna()


# ============================================================
# 7. AGE-STRATIFIED PREVALENCE -- CORRECTED
# ============================================================

def age_stratified_prevalence(df):
    """
    Extract national age-specific prevalence.

    Preserve Race, Sex, and Dual Status subgroups.
    Do not combine overlapping demographic populations.
    """

    ages = df[
        (df["Bene_Geo_Lvl"] == "National")
        & df["Bene_Age_Lvl"].isin(["<65", "65+"])
        & df["Bene_Demo_Lvl"].isin(
            ["Race", "Sex", "Dual Status"]
        )
    ].copy()

    ages["Prevalence_pct"] = ages["Prvlnc"] * 100

    ages = ages[
        [
            "Bene_Cond",
            "Bene_Age_Lvl",
            "Bene_Demo_Lvl",
            "Bene_Demo_Desc",
            "Prevalence_pct",
        ]
    ].dropna(
        subset=["Prevalence_pct"]
    )

    return ages.sort_values(
        [
            "Bene_Cond",
            "Bene_Age_Lvl",
            "Bene_Demo_Lvl",
            "Bene_Demo_Desc",
        ]
    ).reset_index(drop=True)


# ============================================================
# 8. GENERATE VISUALIZATIONS
# ============================================================

def draw_charts(prev, util, ext):
    """Save three descriptive population health charts."""

    chosen = [
        "Diabetes",
        "Hypertension",
        "COPD",
        "Heart Failure",
        "Depression",
    ]

    # --------------------------------------------------------
    # FIGURE 1: CHRONIC DISEASE PREVALENCE
    # --------------------------------------------------------

    plot = prev[
        prev["Bene_Cond"].isin(chosen)
    ]

    wide = plot.pivot(
        index="Bene_Cond",
        columns="Bene_Geo_Desc",
        values="Prevalence_pct",
    ).reindex(chosen)

    ax = wide.plot(
        kind="bar",
        figsize=(11, 5.5),
        width=0.8,
    )

    ax.set(
        title=(
            "Chronic Condition Prevalence Among "
            "Medicare FFS Beneficiaries"
        ),
        xlabel="Chronic condition",
        ylabel="Prevalence (%)",
    )

    ax.tick_params(
        axis="x",
        rotation=25,
    )

    ax.legend(
        title="Geography",
        fontsize=8,
    )

    ax.figure.tight_layout()

    ax.figure.savefig(
        FIG / "prevalence_selected_conditions.png",
        dpi=160,
    )

    plt.close(ax.figure)

    # --------------------------------------------------------
    # FIGURE 2: MEDICARE SPENDING
    # --------------------------------------------------------

    spending = util[
        (util["Bene_Geo_Desc"] == "National")
        & util["Bene_Cond"].isin(chosen)
    ]

    spending = (
        spending
        .set_index("Bene_Cond")["Tot_Mdcr_Stdzd_Pymt_PC"]
        .reindex(chosen)
        .dropna()
    )

    ax = spending.plot.bar(
        figsize=(9, 5)
    )

    ax.set(
        title=(
            "Standardized Medicare "
            "Per-Capita Payments (National)"
        ),
        xlabel="Chronic condition",
        ylabel="Payments per beneficiary (USD)",
    )

    ax.tick_params(
        axis="x",
        rotation=25,
    )

    ax.figure.tight_layout()

    ax.figure.savefig(
        FIG / "medicare_spending.png",
        dpi=160,
    )

    plt.close(ax.figure)

    # --------------------------------------------------------
    # FIGURE 3: STATE-TO-NATIONAL PREVALENCE DIFFERENCES
    # --------------------------------------------------------

    ranking = ext.nlargest(
        10,
        "Highest_vs_National_pp",
    ).sort_values(
        "Highest_vs_National_pp"
    )

    ax = ranking.plot.barh(
        x="Bene_Cond",
        y="Highest_vs_National_pp",
        legend=False,
        figsize=(10, 6),
    )

    ax.set(
        title=(
            "Largest Positive State-to-National Differences\n"
            "in Chronic Disease Prevalence"
        ),
        xlabel=(
            "Difference from national prevalence "
            "(percentage points)"
        ),
        ylabel="Chronic condition",
    )

    ax.figure.tight_layout()

    ax.figure.savefig(
        FIG / "state_prevalence_gap.png",
        dpi=160,
    )

    plt.close(ax.figure)


# ============================================================
# 9. MAIN ANALYSIS WORKFLOW
# ============================================================

def main():
    """Process data, export tables, and generate figures."""

    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    FIG.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    prev = prevalence_comparison(df)
    util = utilization_comparison(df)

    ext = extrema(df)
    sex = extrema(df, "Sex")
    race = extrema(df, "Race")

    ages = age_stratified_prevalence(df)

    tables = {
        "condition_prevalence_by_geography": prev,
        "medicare_utilization": util,
        "state_prevalence_extremes": ext,
        "state_prevalence_extremes_by_sex": sex,
        "state_prevalence_extremes_by_race": race,
        "prevalence_by_race": subgroup_prevalence(
            df, "Race"
        ),
        "prevalence_by_age": ages,
    }

    for name, table in tables.items():
        table.to_csv(
            OUT / f"{name}.csv",
            index=False,
        )

    draw_charts(prev, util, ext)

    print(
        f"Processed {len(df):,} aggregate records, "
        f"{df['Bene_Cond'].nunique()} conditions; "
        f"wrote {len(tables)} summary CSV files "
        "and 3 PNG figures."
    )

    print(
        "Age-stratified prevalence records:",
        len(ages),
    )

    print(
        "Missing utilization entries are retained "
        "as missing rather than zeros."
    )


# ============================================================
# 10. EXECUTE MAIN FUNCTION
# ============================================================

if __name__ == "__main__":
    main()
