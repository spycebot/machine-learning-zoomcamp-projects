# Harmonise Stack Overflow Developer Survey 2023-2025 for a UK/EU salary model.
# Usage:
#   df = pd.concat([harmonise(df_2023, 2023),
#                   harmonise(df_2024, 2024),
#                   harmonise(df_2025, 2025)], ignore_index=True)

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Scope: EU-27 + United Kingdom (country names as spelled in the survey)
# ---------------------------------------------------------------------------
UK_EU_COUNTRIES = [
    'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
    'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary',
    'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
    'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
    'Spain', 'Sweden', 'United Kingdom of Great Britain and Northern Ireland',
]

# Languages present in all three surveys (2023-2025), most common first
COMMON_LANGUAGES = [
    'JavaScript', 'HTML/CSS', 'SQL', 'Python', 'Bash/Shell (all shells)',
    'TypeScript', 'Java', 'C#', 'C++', 'PowerShell', 'C', 'PHP', 'Go',
    'Rust', 'Kotlin', 'Lua', 'Dart', 'Ruby', 'Swift', 'R',
]

# Ordered categories (useful for ordinal encoding / sorted plots)
ORDINAL_ORDERS = {
    'OrgSize': [
        'Just me - I am a freelancer, sole proprietor, etc.',
        'Less than 20 employees', '20 to 99 employees', '100 to 499 employees',
        '500 to 999 employees', '1,000 to 4,999 employees',
        '5,000 to 9,999 employees', '10,000 or more employees',
    ],
    'Age': [
        'Under 18 years old', '18-24 years old', '25-34 years old',
        '35-44 years old', '45-54 years old', '55-64 years old',
        '65 years or older',
    ],
    'EdLevel': [
        'Primary/elementary school',
        'Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)',
        'Some college/university study without earning a degree',
        'Associate degree (A.A., A.S., etc.)',
        'Bachelor’s degree (B.A., B.S., B.Eng., etc.)',
        'Master’s degree (M.A., M.S., M.Eng., MBA, etc.)',
        'Professional degree (JD, MD, Ph.D, Ed.D, etc.)',
    ],
}

# DevType: map every label from 2023-2025 onto one common role list
_DEVTYPE_MAP = {
    # unchanged developer roles
    'Developer, full-stack': 'Developer, full-stack',
    'Developer, back-end': 'Developer, back-end',
    'Developer, front-end': 'Developer, front-end',
    'Developer, mobile': 'Developer, mobile',
    'Developer, desktop or enterprise applications': 'Developer, desktop or enterprise',
    'Developer, embedded applications or devices': 'Developer, embedded',
    'Developer, game or graphics': 'Developer, game or graphics',
    'Developer, QA or test': 'Developer, QA or test',
    # data & AI
    'Data scientist or machine learning specialist': 'Data science / AI-ML',
    'Data scientist': 'Data science / AI-ML',
    'AI/ML engineer': 'Data science / AI-ML',
    'Applied scientist': 'Data science / AI-ML',
    'Developer, AI': 'Data science / AI-ML',
    'Developer, AI apps or physical AI': 'Data science / AI-ML',
    'Engineer, data': 'Data engineer',
    'Data engineer': 'Data engineer',
    'Data or business analyst': 'Analyst',
    'Financial analyst or engineer': 'Analyst',
    # infrastructure & security
    'DevOps specialist': 'DevOps / cloud / SRE',
    'DevOps engineer or professional': 'DevOps / cloud / SRE',
    'Engineer, site reliability': 'DevOps / cloud / SRE',
    'Cloud infrastructure engineer': 'DevOps / cloud / SRE',
    'System administrator': 'Sysadmin / DBA',
    'Database administrator': 'Sysadmin / DBA',
    'Database administrator or engineer': 'Sysadmin / DBA',
    'Security professional': 'Security',
    'Cybersecurity or InfoSec professional': 'Security',
    # management & leadership
    'Engineering manager': 'Manager',
    'Project manager': 'Manager',
    'Product manager': 'Manager',
    'Senior Executive (C-Suite, VP, etc.)': 'Executive / founder',
    'Senior executive (C-suite, VP, etc.)': 'Executive / founder',
    'Founder, technology or otherwise': 'Executive / founder',
    'Architect, software or solutions': 'Architect',  # 2025 only
    # research
    'Academic researcher': 'Research',
    'Scientist': 'Research',
    'Research & Development role': 'Research',
    # not working as a developer
    'Student': 'Student',
    'Retired': 'Retired',
    # everything else (Blockchain, Designer, UX, Educator, Hardware Engineer,
    # Developer Advocate/Experience, Marketing, Support, "Other ...")
}

_DEV_FAMILY = {
    'Developer, full-stack': 'Software developer',
    'Developer, back-end': 'Software developer',
    'Developer, front-end': 'Software developer',
    'Developer, mobile': 'Software developer',
    'Developer, desktop or enterprise': 'Software developer',
    'Developer, embedded': 'Software developer',
    'Developer, game or graphics': 'Software developer',
    'Developer, QA or test': 'Software developer',
    'Data science / AI-ML': 'Data & AI',
    'Data engineer': 'Data & AI',
    'Analyst': 'Data & AI',
    'DevOps / cloud / SRE': 'Infrastructure & security',
    'Sysadmin / DBA': 'Infrastructure & security',
    'Security': 'Infrastructure & security',
    'Manager': 'Management & leadership',
    'Executive / founder': 'Management & leadership',
    'Architect': 'Software developer',  # 2025-only label; earlier architects
                                        # most likely chose a developer role
    'Research': 'Research',
    'Student': 'Not working as developer',
    'Retired': 'Not working as developer',
    'Other': 'Other',
}


def _years_to_float(s):
    """Convert YearsCode / YearsCodePro / WorkExp to float.
    2023/24 store text such as 'Less than 1 year' and 'More than 50 years'."""
    return pd.to_numeric(
        s.replace({'Less than 1 year': 0.5, 'More than 50 years': 51}),
        errors='coerce',
    )


def _primary_employment(value):
    """Collapse 2023/24 multi-select Employment to one 2025-style category."""
    if pd.isna(value):
        return np.nan
    items = value.split(';')
    if 'Employed, full-time' in items:
        return 'Employed'
    if 'Independent contractor, freelancer, or self-employed' in items:
        return 'Independent contractor, freelancer, or self-employed'
    if 'Employed, part-time' in items:
        return 'Employed'
    if any(i.startswith('Student') for i in items):
        return 'Student'
    if any(i.startswith('Not employed') for i in items):
        return 'Not employed'
    if 'Retired' in items:
        return 'Retired'
    return 'I prefer not to say'


def harmonise(df, year, uk_eu_only=True, languages=COMMON_LANGUAGES):
    """Return a harmonised copy of one Stack Overflow survey year (2023-2025).

    Output columns are identical for every year, so the results can be
    combined with pd.concat. ConvertedCompYearly (USD) is kept as the target.

    Parameters
    ----------
    df : DataFrame read from the survey CSV for that year
    year : 2023, 2024 or 2025
    uk_eu_only : keep only respondents in the EU-27 + United Kingdom
    languages : languages to one-hot encode as lang_<name> (None to skip)
    """
    if year not in (2023, 2024, 2025):
        raise ValueError('year must be 2023, 2024 or 2025')

    df = df.copy()
    if uk_eu_only:
        df = df[df['Country'].isin(UK_EU_COUNTRIES)]

    out = pd.DataFrame(index=df.index)
    out['year'] = year
    out['ResponseId'] = df['ResponseId']
    out['Country'] = df['Country']

    # --- columns that only need light relabelling -------------------------
    out['MainBranch'] = df['MainBranch']
    out['Age'] = df['Age'].replace({'Prefer not to say': np.nan})
    out['EdLevel'] = df['EdLevel'].replace({
        'Something else': 'Other',
        'Other (please specify):': 'Other',
    })
    out['ICorPM'] = df['ICorPM']
    out['AISent'] = df['AISent']

    # --- Employment: 2023/24 multi-select -> single 2025 category ----------
    if year == 2025:
        out['Employment'] = df['Employment']
    else:
        out['Employment'] = df['Employment'].map(_primary_employment)

    # --- OrgSize: merge small-company bands into 'Less than 20 employees' --
    out['OrgSize'] = df['OrgSize'].replace({
        '2 to 9 employees': 'Less than 20 employees',
        '10 to 19 employees': 'Less than 20 employees',
        'I don’t know': np.nan,
    })

    # --- RemoteWork: 5 options in 2025 -> Remote / Hybrid / In-person ------
    out['RemoteWork'] = df['RemoteWork'].map(
        lambda v: v if pd.isna(v) or v in ('Remote', 'In-person') else 'Hybrid'
    )

    # --- AISelect: 2025 'Yes, I use AI tools daily/weekly/...' -> 'Yes' ----
    out['AISelect'] = df['AISelect'].map(
        lambda v: 'Yes' if isinstance(v, str) and v.startswith('Yes') else v
    )

    # --- Industry: 2024 and 2025 share a list; 2023 uses another ----------
    out['Industry'] = np.nan if year == 2023 else df['Industry'].replace({'Other:': 'Other'})

    # --- DevType: common role list + broader family -----------------------
    out['DevRole'] = df['DevType'].map(_DEVTYPE_MAP)
    out.loc[df['DevType'].notna() & out['DevRole'].isna(), 'DevRole'] = 'Other'
    out['DevFamily'] = out['DevRole'].map(_DEV_FAMILY)

    # --- Experience -------------------------------------------------------
    out['YearsCode'] = _years_to_float(df['YearsCode'])
    work_exp = pd.to_numeric(df['WorkExp'], errors='coerce')
    if year in (2023, 2024):
        # WorkExp is only ~half filled in 2023/24: fall back on YearsCodePro
        work_exp = work_exp.fillna(_years_to_float(df['YearsCodePro']))
    out['WorkExp'] = work_exp.clip(upper=50)    # 2025 allows up to 100
    out['YearsCode'] = out['YearsCode'].clip(upper=51)

    # --- Languages: one-hot for languages present in every year -----------
    if languages:
        worked = df['LanguageHaveWorkedWith']
        for lang in languages:
            out[f'lang_{lang}'] = worked.str.split(';').map(
                lambda items: lang in items if isinstance(items, list) else np.nan
            ).astype('float')

    # --- Target -----------------------------------------------------------
    out['ConvertedCompYearly'] = pd.to_numeric(df['ConvertedCompYearly'], errors='coerce')

    return out.reset_index(drop=True)