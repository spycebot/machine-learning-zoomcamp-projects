# Machine Learning Zoomcamp Projects

Created 06 NOV 2026

Machine Learning Zoomcamp is a deep dive into ML Principles. These projects are requisite for the certificate.

## Course information

[Course Description and Syllabus](https://github.com/DataTalksClub/machine-learning-zoomcamp/tree/main)

### Project Criteria

[General Criteria](https://github.com/DataTalksClub/machine-learning-zoomcamp/tree/main/projects)

[2026 Cohort Midterm Project Criteria]()

[Midterm Project Submission](https://courses.datatalks.club/ml-zoomcamp-2026/project/midterm)


This is what you need to do for each project

1. Think of a problem that's interesting for you and find a dataset for that
1. Describe this problem and explain how a model could be used
Prepare the data and doing EDA, analyze important features
1. Train multiple models, tune their performance and select the best model
1. Export the notebook into a script
1. Put your model into a web service and deploy it locally with Docker
1. Bonus points for deploying the service to the cloud


### Launching the Notebook

The Jupyter Notebook for the exercises was launched by the fllowing command on the bash shell in the GitHub Codespace:

@spycebot ➜ /workspaces/machine-learning-zoomcamp-projects (main) $ jupyter lab

However, for the course exercises notebook, the following command is required:

$ jupyter notebook

Similarly, previously installed packages had to be installed one-by-one

In: !pip install pandas
In: !pip install matplotlib
In: !pip install seaborn


### Considering the Problem

Right now, the problem of finding an employer in the computer industry who is willing to employ me is the most interesting. 
Utilising the tools available to me, I found many potential datasets with the potential to address this problem. Through iterative question and answer, I have settled on Stack Overflow Developer Survey, filtered to UK and EU respondents, with country as a feature, as the primary dataset. A few country-level features from Eurostat or the OECD, such as a price-level index or GDP per capita may provide supplementary features as well.


### Problem Statement

The problem is that job seekers are generally distressed, being under both time and financial pressures to find a job. Job seekers are also the target of a great deal of marketing, which offers "common sense" jobseeker advice which may or may not be objectively true.

This project seeks to address that problem by providing a clear and objective method for evaluating jobs and jobseekers. Having such a tool, jobseekers can make a more well informed determination regarding their own prospects in the job market.


### Data Preparation and Exploratory Data Analysis

Clear initial trend: Each year, fewer and fewer people are taking the survey, while each year, the survey has more and more questions (df.describe()).

- **2025-only roles**: "Architect" and "Retired" appear only in 2025 source data set. Architect has been grouped with the software-developer family and kept as its own `DevRole`.
- **Unclassified roles in 2023**: 4,392 respondents have no `DevType`, so their `DevRole` is missing.
- **Experience rises in 2025**: median YearsCode is 15 in 2025 against 12 in the earlier years. This probably reflects a change in who answered or how the question was worded, rather than real change, so keep year as a feature.
- **No `Industry` in 2023**: if you train on all three years, either drop Industry or let your model handle missing values natively. XGBoost and HistGradientBoostingRegressor both do. Linear regression requires that the gaps are filled first. The `harmonise.py` function populates 2023 data industry field with `NaN`.
- **Ordering for plots and linear models**: ORDINAL_ORDERS in the file gives the correct order for OrgSize, Age and EdLevel.

#### Harmonising source data from three years

`harmonise.py`: Written so that three years of StackOverflow survey data now produce the same 38 columns, and they combine into one table of 73,606 UK/EU rows.

In: 
    from harmonise import harmonise

to bring harmonise.py into the notebook.

**What the `harmonise()` function does**

- **Rows**: Keeps only respondents in the 27 EU member states plus the UK. Pass `uk_eu_only=False` to keep every country.
- **Kept as they are**: `year`, `Country`, `MainBranch` and `ICorPM`, with `ConvertedCompYearly` (US dollars) as the target. `Age` and `AISent` are also unchanged, except that "Prefer not to say" in `Age` becomes missing.
- **EdLevel**: "Something else" and "Other (please specify):" become "Other".
- **Employment**: the 2023/24 multiple answers become a single answer, with full-time employment taking priority, then contractor.
- **OrgSize**: "2 to 9" and "10 to 19" become "Less than 20 employees", and "I don’t know" becomes missing.
- **RemoteWork**: Reduced to Remote, Hybrid or In-person.
- **AISelect**: Reduced to Yes or No.
- **DevType becomes two columns: DevRole, with 21 role names shared across years, and DevFamily, with 7 broad groups.
- **Industry**: Kept for 2024 and 2025 (confirmed the two category lists are identical) and missing for 2023.
-- WorkExp and YearsCode:
Converted to numbers, with "Less than 1 year" set to 0.5 and "More than 50 years" to 51.
-- Missing WorkExp values in 2023/24 are filled from YearsCodePro.
-- Capped at 50 (WorkExp) and 51 (YearsCode), because 2025 allows answers up to 100.
- **Languages**: 20 `lang_*` columns, each set to 1 or 0 and missing where the respondent skipped the question. Checked that all 20 languages appear in every year.


### Training of Multiple Models


### Export Notebook to a Scipt


### Place Model into a Web Service


### Deploy Web Service Locally with Docker


### Deploy Web Service to the Cloud


