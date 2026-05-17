# Data Sources

This document lists the data sources used across this repository, with connection examples.

---

## 1. U.S. Census Bureau — American Community Survey (ACS)

The ACS is an annual survey conducted by the U.S. Census Bureau that provides detailed demographic, social, economic, and housing data for every community in the United States. Data is available at many geographic levels (state, county, tract, block group) and includes thousands of variables covering population, income, employment, education, race, and more.

**How it works:** You make HTTP GET requests to the Census REST API, specifying the dataset (e.g. `acs/acs5`), the variables you want, and the geography. Results come back as JSON arrays.

- **API Documentation:** [https://www.census.gov/data/developers/data-sets.html](https://www.census.gov/data/developers/data-sets.html)
- **Variable Explorer:** [https://api.census.gov/data/2022/acs/acs5/variables.html](https://api.census.gov/data/2022/acs/acs5/variables.html)
- **API Key Signup:** [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
- **API Key used in this repo:** `942e0a44c121ca03ced84b727df9b004f1f1367d`

```python
from census import Census

CENSUS_API_KEY = "942e0a44c121ca03ced84b727df9b004f1f1367d"
c = Census(CENSUS_API_KEY)

# Fetch total population (B01003_001E) by state from ACS 5-Year 2022
data = c.acs5.state(
    fields=("NAME", "B01003_001E"),
    state_fips="*",
    year=2022
)

# data is a list of dicts, e.g.:
# [{'NAME': 'Alabama', 'B01003_001E': 5024279, 'state': '01'}, ...]
```

**Alternative — direct REST API (no library needed):**

```python
import requests

CENSUS_API_KEY = "942e0a44c121ca03ced84b727df9b004f1f1367d"

url = "https://api.census.gov/data/2022/acs/acs5"
params = {
    "get": "NAME,B01003_001E",   # Total Population
    "for": "state:*",            # All states
    "key": CENSUS_API_KEY
}

response = requests.get(url, params=params)
data = response.json()
# First row is headers, rest is data
# [['NAME', 'B01003_001E', 'state'], ['Alabama', '5024279', '01'], ...]
```

### ACS Public Use Microdata Sample (PUMS)

The ACS PUMS files provide person- and household-level survey microdata with statistical weights. This repository uses 2024 ACS 1-year PUMS in `population_work_2.ipynb` for rectangular proportion views of disjoint race/ethnicity categories, SNAP-recipient household population, and a modeled federal income-tax proxy.

- **PUMS data access:** [https://www.census.gov/programs-surveys/acs/microdata/access.html](https://www.census.gov/programs-surveys/acs/microdata/access.html)
- **Microdata API guide:** [https://www.census.gov/data/developers/guidance/microdata-api-user-guide.Types_of_Microdata_API_Queries.html](https://www.census.gov/data/developers/guidance/microdata-api-user-guide.Types_of_Microdata_API_Queries.html)
- **2024 ACS 1-year PUMS variables:** [https://api.census.gov/data/2024/acs/acs1/pums/variables.html](https://api.census.gov/data/2024/acs/acs1/pums/variables.html)

Important usage notes:

- Use `PWGTP` as the person weight when estimating counts of people.
- `HISP` and `RAC1P` can be combined into disjoint categories by assigning all Hispanic/Latino people first, then classifying the remaining non-Hispanic population by race.
- `FS` identifies whether a person lives in a household that received Food Stamps/SNAP in the past 12 months.
- `PINCP` is person income; dollar values should be adjusted with `ADJINC` when needed.

Tax caveat: IRS individual tax statistics do not directly report tax payments by race/ethnicity because tax returns do not collect race/ethnicity. The tax visualization in `population_work_2.ipynb` is therefore a transparent ACS-income-based estimate, not filed-return tax data. Treasury discusses this limitation and imputation approaches here: [https://home.treasury.gov/news/featured-stories/disparities-in-the-benefits-of-tax-expenditures-by-race-and-ethnicity](https://home.treasury.gov/news/featured-stories/disparities-in-the-benefits-of-tax-expenditures-by-race-and-ethnicity).

---

## 2. World Bank — Indicators API v2

The World Bank Indicators API provides access to hundreds of development indicators (GDP, population, life expectancy, trade, etc.) for every country and region in the world. Data spans decades and is updated regularly. No API key is required — it's completely open.

**How it works:** You make GET requests specifying the country (ISO codes or `all`), the indicator code (e.g. `NY.GDP.MKTP.CD` for GDP), and optional filters like date range. Results come back as JSON with a metadata header and a data array.

- **API Documentation:** [https://datahelpdesk.worldbank.org/knowledgebase/articles/889392](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- **Indicator List:** [https://api.worldbank.org/v2/indicator?format=json&per_page=50](https://api.worldbank.org/v2/indicator?format=json&per_page=50)
- **API Key:** None required (open access)

```python
import requests
import pandas as pd

# Fetch GDP (current US$) for all countries, year 2023
url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
params = {
    "format": "json",
    "per_page": 300,
    "date": "2023"
}

response = requests.get(url, params=params)
raw = response.json()

# raw[0] = metadata, raw[1] = list of records
records = raw[1]

# Build a clean DataFrame
rows = []
for r in records:
    if r["value"] is not None:
        rows.append({
            "country": r["country"]["value"],
            "iso3": r["countryiso3code"],
            "year": r["date"],
            "gdp": r["value"]
        })

df = pd.DataFrame(rows)
print(df.sort_values("gdp", ascending=False).head(10))
```

**Common indicator codes:**

| Code | Description |
|------|-------------|
| `NY.GDP.MKTP.CD` | GDP (current US$) |
| `NY.GDP.PCAP.CD` | GDP per capita (current US$) |
| `SP.POP.TOTL` | Total Population |
| `SP.DYN.LE00.IN` | Life Expectancy at Birth |
| `SI.POV.DDAY` | Poverty Headcount Ratio |
| `SL.UEM.TOTL.ZS` | Unemployment Rate |
| `DT.ODA.ODAT.CD` | Net ODA Received (current US$) |
| `NY.GDP.PETR.RT.ZS` | Oil rents (% of GDP) |
| `NY.GDP.NGAS.RT.ZS` | Natural gas rents (% of GDP) |
| `NY.GDP.COAL.RT.ZS` | Coal rents (% of GDP) |
| `NY.GDP.FRST.RT.ZS` | Forest rents (% of GDP) |
| `SL.TLF.CACT.ZS` | Labour Force Participation Rate, total (% of pop. 15+) |
| `SL.TLF.CACT.MA.ZS` | Labour Force Participation Rate, male (%) |
| `SL.TLF.CACT.FE.ZS` | Labour Force Participation Rate, female (%) |
| `NV.AGR.TOTL.ZS` | Agriculture, value added (% of GDP) |
| `NV.IND.TOTL.ZS` | Industry, value added (% of GDP) |
| `NV.SRV.TOTL.ZS` | Services, value added (% of GDP) |

---

## 3. Eurostat — Statistics JSON API

Eurostat is the statistical office of the European Union. Its JSON-stat REST API provides open access to hundreds of datasets covering demographics, economy, crime, migration, and more for all EU/EEA countries. **No API key is required** — all data is freely available.

**How it works:** You make HTTP GET requests specifying the dataset code, output format (`JSON`), and filter dimensions (time period, geography, category, etc.). Results come back in JSON-stat 2.0 format with a flat `value` object keyed by position indices, plus `dimension` metadata to decode them.

- **API Documentation:** [https://wikis.ec.europa.eu/display/EUROSTATHELP/API+Statistics](https://wikis.ec.europa.eu/display/EUROSTATHELP/API+Statistics)
- **Data Browser (find dataset codes):** [https://ec.europa.eu/eurostat/databrowser/](https://ec.europa.eu/eurostat/databrowser/)
- **API Key:** None required (open access)

```python
import requests
import pandas as pd

# ── Crime: intentional homicide per 100k inhabitants for major EU countries ──
EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

COUNTRIES = ["DE", "FR", "IT", "ES", "NL", "BE", "SE", "AT", "PL", "PT",
             "CZ", "DK", "FI", "IE", "EL", "RO", "HU", "BG", "HR"]

crime_url = f"{EUROSTAT_BASE}/crim_off_cat"
crime_params = {
    "format": "JSON",
    "lang": "en",
    "sinceTimePeriod": "2022",
    "iccs": "ICCS0101",       # Intentional homicide
    "unit": "P_HTHAB",        # Per 100 000 inhabitants
    "geo": COUNTRIES,
}

resp = requests.get(crime_url, params=crime_params)
data = resp.json()

# Decode JSON-stat → DataFrame
geo_labels = data["dimension"]["geo"]["category"]["label"]   # {"DE": "Germany", ...}
geo_index  = data["dimension"]["geo"]["category"]["index"]   # {"DE": 0, ...}
time_index = data["dimension"]["time"]["category"]["index"]  # {"2022": 0, "2023": 1}
n_geo  = len(geo_index)
n_time = len(time_index)

rows = []
for geo_code, gi in geo_index.items():
    for year, ti in time_index.items():
        pos = str(gi * n_time + ti)
        val = data["value"].get(pos)
        if val is not None:
            rows.append({"country": geo_labels[geo_code], "iso2": geo_code,
                         "year": year, "homicide_rate": val})

df_crime = pd.DataFrame(rows)
print(df_crime.sort_values("homicide_rate", ascending=False).head(10))
```

```python
# ── Migration: total immigration by country ──
migr_url = f"{EUROSTAT_BASE}/migr_imm1ctz"
migr_params = {
    "format": "JSON",
    "lang": "en",
    "sinceTimePeriod": "2022",
    "citizen": "TOTAL",
    "age": "TOTAL",
    "sex": "T",
    "geo": COUNTRIES,
}

resp = requests.get(migr_url, params=migr_params)
data = resp.json()

# Same decoding pattern as above
geo_labels = data["dimension"]["geo"]["category"]["label"]
geo_index  = data["dimension"]["geo"]["category"]["index"]
time_index = data["dimension"]["time"]["category"]["index"]
n_geo  = len(geo_index)
n_time = len(time_index)

rows = []
for geo_code, gi in geo_index.items():
    for year, ti in time_index.items():
        pos = str(gi * n_time + ti)
        val = data["value"].get(pos)
        if val is not None:
            rows.append({"country": geo_labels[geo_code], "iso2": geo_code,
                         "year": year, "immigrants": val})

df_migr = pd.DataFrame(rows)
print(df_migr.sort_values("immigrants", ascending=False).head(10))
```

**Common dataset codes:**

| Code | Description |
|------|-------------|
| `crim_off_cat` | Police-recorded offences by category |
| `migr_imm1ctz` | Immigration by citizenship, age, sex |
| `migr_asyappctza` | Asylum applicants by citizenship |
| `demo_pjan` | Population on 1 January |
| `nama_10_gdp` | GDP and main components |

---

## 4. Bureau of Economic Analysis (BEA) — GDP-by-Industry and Input-Output APIs

The BEA provides detailed economic accounts for the U.S. economy, including GDP broken down by industry sector (value added, gross output, compensation, etc.) and input-output accounts showing production relationships among industries and commodities. The REST API requires a **free API key** obtained by registering.

**How it works:** You make HTTP GET requests specifying the `DataSetName` (e.g. `GDPbyIndustry`), `TableID`, `Frequency`, `Year`, and `Industry` filters. Results come back as JSON with a `Data` array of records.

- **API Documentation:** [https://apps.bea.gov/API/docs/index.htm](https://apps.bea.gov/API/docs/index.htm)
- **API Key Signup:** [https://apps.bea.gov/api/signup/](https://apps.bea.gov/api/signup/)
- **Input-Output Accounts:** [https://www.bea.gov/data/industries/input-output-accounts-data](https://www.bea.gov/data/industries/input-output-accounts-data)
- **API Key used in this repo:** `F784B0EB-9FE2-4CFD-B650-2F510B52025C`

```python
import requests
import pandas as pd

BEA_API_KEY = "F784B0EB-9FE2-4CFD-B650-2F510B52025C"

url = "https://apps.bea.gov/api/data/"
params = {
    "UserID":      BEA_API_KEY,
    "method":      "GetData",
    "DataSetName": "GDPbyIndustry",
    "TableID":     "1",          # Value Added by Industry
    "Frequency":   "A",          # Annual
    "Year":        "2022,2023",
    "Industry":    "ALL",
    "ResultFormat":"JSON",
}

response = requests.get(url, params=params)
data = response.json()

# Navigate to the data records
records = data["BEAAPI"]["Results"]["Data"]
df = pd.DataFrame(records)
print(df[["Year", "IndustryDescription", "DataValue"]].head(20))
```

**Common parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| `TableID` | `1` | Value Added by Industry |
| `TableID` | `5` | Gross Output by Industry |
| `TableID` | `6` | Components of Value Added by Industry |
| `TableID` | `10` | Real Value Added by Industry |
| `Frequency` | `A`, `Q` | Annual, Quarterly |
| `Industry` | `ALL`, `11`, `21`, `31-33`, etc. | All industries or specific NAICS codes |

### BEA Input-Output Accounts

The `InputOutput` API dataset provides make tables, use tables, and requirements tables. Use tables show how the supply of commodities is used by industries, final users, government, and exports. Summary-level use tables are one layer below the broad sector level while remaining available annually; the most detailed benchmark tables are much larger and only available for benchmark years.

```python
import requests
import pandas as pd

BEA_API_KEY = "F784B0EB-9FE2-4CFD-B650-2F510B52025C"
url = "https://apps.bea.gov/api/data/"

# 1) Look up official InputOutput table IDs.
params = {
    "UserID": BEA_API_KEY,
    "method": "GetParameterValues",
    "DataSetName": "InputOutput",
    "ParameterName": "TableID",
    "ResultFormat": "JSON",
}
tables = requests.get(url, params=params, timeout=45).json()
table_values = pd.DataFrame(tables["BEAAPI"]["Results"]["ParamValue"])

# 2) Fetch a Use table after selecting a TableID and year.
params = {
    "UserID": BEA_API_KEY,
    "method": "GetData",
    "DataSetName": "InputOutput",
    "TableID": "258",  # Example: Use of Commodities by Industries - Sector
    "Year": "2020",
    "ResultFormat": "JSON",
}
data = requests.get(url, params=params, timeout=45).json()
records = data["BEAAPI"]["Results"]["Data"]
df = pd.DataFrame(records)
print(df[["RowDescr", "ColDescr", "DataValue"]].head())
```

### Local Eora-Style Czech Sector Flows

`sectors.ipynb` uses local Eora-style sector files in `/Users/pstaif/Desktop/Econ Ultimate Map/data/` instead of a live BEA API call. The flow matrix is a labeled Czech Republic intermediate transactions table for 2022; rows are source sectors and columns are destination sectors.

| File | Use |
|------|-----|
| `CZE_Z_intermediate_2022_labeled.csv` | Numeric source-by-destination intermediate sector flows |
| `CZE_sector_codebook.csv` | Sector code-to-label mapping |
| `Eora26Structure.xlsx` | Eora26 classification/layout reference |

The primary-sector Sankey cells use rows `CZE_A01`, `CZE_A02`, `CZE_A03`, and `CZE_B05` through `CZE_B09` flowing to all positive destination sectors, with smaller destinations grouped as `Other sectors`.

---

## 5. OECD — Input-Output & Labour Statistics

The OECD provides harmonised economic statistics across member countries, including Inter-Country Input-Output (ICIO) tables and Labour Force Statistics. Data can be accessed via the OECD Data Explorer REST API or downloaded as CSV/SDMX.

- **Data Explorer:** [https://data-explorer.oecd.org/](https://data-explorer.oecd.org/)
- **ICIO Tables:** [https://www.oecd.org/sti/ind/inter-country-input-output-tables.htm](https://www.oecd.org/sti/ind/inter-country-input-output-tables.htm)
- **API Documentation:** [https://data-explorer.oecd.org/help](https://data-explorer.oecd.org/help)

```python
import requests
import pandas as pd

# Example: fetch labour force statistics
url = "https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_LFS@DF_LFS_INDIC,1.0/USA..._T._T.Y._T.A"
headers = {"Accept": "application/vnd.sdmx.data+csv;version=2"}
r = requests.get(url, headers=headers, timeout=30)
df = pd.read_csv(io.StringIO(r.text))
print(df.head())
```

**Key datasets used in this repo:**

| Dataset | Description |
|---------|-------------|
| ICIO Tables | Inter-industry intermediate consumption flows (45 ISIC Rev.4 sectors × 76 countries) |
| LFS (Labour Force Survey) | Employment, hours worked, earnings by age, gender, industry |
| EAG (Education at a Glance) | Earnings by education level, age, and gender |

---

## 6. OpenStreetMap — Overpass API

OpenStreetMap (OSM) is a collaborative, open-source map of the world. The **Overpass API** allows programmatic queries against the full OSM database to extract geographic features (roads, railways, land use, buildings, etc.) by tag, area, or bounding box. **No API key is required.**

**How it works:** You POST an Overpass QL query to the API endpoint. Results come back as JSON with an `elements` array containing nodes, ways, and relations.

- **Overpass Turbo (interactive):** [https://overpass-turbo.eu/](https://overpass-turbo.eu/)
- **API Endpoint:** `https://overpass-api.de/api/interpreter`
- **Wiki (tag reference):** [https://wiki.openstreetmap.org/wiki/Map_features](https://wiki.openstreetmap.org/wiki/Map_features)
- **API Key:** None required (open access, but please be polite with rate limits)

```python
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Count major roads in a bounding box (south, west, north, east)
query = """
[out:json][timeout:60];
(
  nwr["highway"~"motorway|trunk|primary"](5.6,97.3,20.5,105.7);
);
out count;
"""

r = requests.post(OVERPASS_URL, data={"data": query}, timeout=120)
data = r.json()
count = int(data["elements"][0]["tags"]["total"])
print(f"Major roads: {count}")
```

**Common tag filters used in this repo:**

| Tag Filter | Description |
|-----------|-------------|
| `"highway"~"motorway\|trunk\|primary"` | Major roads (motorways, trunk, primary) |
| `"railway"="rail"` | Railway lines |
| `"landuse"="industrial"` | Industrial land use zones |
| `"landuse"="quarry"` | Mining / quarry sites |
| `"landuse"="farmland"` | Agricultural farmland |
| `"landuse"="farmyard"` | Farm building complexes |
