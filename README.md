# PANGO Lineage -> WHO Label Conversion for COVID-19 Analysis

This project aims to provide a comprehensive conversion scheme that maps PANGO lineages (like `B.1.1.529` and `AY.2`) to their corresponding WHO labels (like `Omicron` and `Delta`).

The ability to swiftly convert between PANGO lineages and WHO labels can streamline data analysis, facilitating broader COVID-19 variant-based studies that bridge the gap between scientific research and public discourse.

For instance, utilising our mapping allows for the correct labeling of more than 85% of [GISAID EpiCoV](https://gisaid.org/) records (tested with over 200k Australia entries). The remaining unlabeled records may belong to recombinant lineages, newly identified lineages, lineages not labeled by WHO, or records without a lineage designation.

<details>
  <summary>Supported WHO Labels</summary>
  <br>
  Alpha, Beta, Delta, Epsilon, Eta, Gamma, Iota, Kappa, Lambda, Mu, Omicron
  <br><br>
</details>

<details>
  <summary>Supported PANGO Lineages</summary>
  <br>
  All key lineages on <a href="https://github.com/cov-lineages/pango-designation">Cov-Lineages dataset</a> and <a href="https://github.com/corneliusroemer/pango-sequences">PANGO consensus sequences dataset</a>.<br><br>
</details>

<details>
  <summary>What are WHO Labels?</summary>
  <br>
  WHO label is a standardized nomenclature used by the World Health Organization (WHO) to classify and refer to different COVID-19 variants. By utilising Greek alphabets (e.g., Alpha, Beta), it simplifies communication and help the general public, media, and health officials easily understand and refer to these variants.
  <br><br>
</details>

<details>
  <summary>Who are PANGO Lineages?</summary>
  <br>
  PANGO (Phylogenetic Assignment of Named Global Outbreak) lineages are a system for naming and tracking the COVID-19 lineages. These lineages can have shorter alias names to simplify the representation of lineage names that can become quite lengthy as new sublineages are identified.
  <br><br>
</details>

<details>
  <summary>Lineage Unaliasing</summary>
  <br>
  Unaliasing a PANGO lineage involves mapping an alias back to its original, longer lineage name.
  <br><br>
  For example: An alias like "BA.1" might represent a more complex and longer lineage name such as "B.1.1.529.1". Unaliasing "BA.1" would result in the full designation "B.1.1.529.1".
  <br><br>
</details>

<details>
  <summary>Lineage Alias Mapping</summary>
  <br>
  Alias mapping is the process of finding aliases of a PANGO lineage. This involves identifying the shorter, simplified alias that corresponds to a more complex lineage name in the PANGO system.
  <br><br>
  For example, mapping "B.1.1.529.1" to its shorter alias "BA.1" would be considered alias mapping.
  <br><br>
</details>

## Approximate Lookup (Core Mapping)

### Data Structure

`mapping.core.csv` contains only the necessary matching rules. For example, `B.1.1.7 -> Alpha` means both `B.1.1.7` and `B.1.1.7.*` map to Alpha. Sublineages of `B.1.1.7` (i.e., `B.1.1.7.*`) are not explicitly stored in the table to allow more generalisation in the lookup process.

```sh
+-----------+------------+
|  Lineage  |  wholabel  |
+-----------+------------+
|  B.1.1.7  |  Alpha     | # B.1.1.7 + B.1.7.* -> Alpha
|  Q        |  Alpha     | # Q + Q.* -> Alpha
|  B.1.351  |  Beta      | # B.1.351 + B.1.351.* -> Beta
|  ...      |  ...       |
+-----------+------------+
```

`mapping.core.sql` provides the same data as `mapping.core.csv` but in the form of SQL statements for replicating the table in a database.

### Lookup Process

PANGO to WHO mapping in this approach is done by approximately matching each record's lineage field in your data with our mapping table. Approximate matching means finding the most specific match.

#### Example Lookup Algorithm with CSV
```py
# dictionary created from CSV transformation
mapping = {
    "BA.2": "Omicron",
    "AY.2": "Delta",
    ...
}

def get_wholabel(lineage):
    # split the lineage by periods to handle hierarchical structure
    cpn = lineage.split('.')
    # iterate over the parts of the lineage in reverse order
    for i in reversed(range(len(cpn))):
        sub = '.'.join(cpn[:i + 1])
        if sub in mapping:
            return mapping[sub]
    # return Unknown if no match is found
    return "Unknown"
```

#### Example Lookup Algorithm with SQL
```sql
LEFT JOIN 
    mapping -- mapping table provided by this repo
ON 
    mapping.lineage = (
        SELECT 
            lineage
        FROM 
            mapping
        WHERE 
            lineage = ori_lineage
            OR ori_lineage LIKE mapping.lineage || '.%'
        ORDER BY 
            lineage DESC
        LIMIT 1
    )
```

Using only strict lookups on core mapping tables will significantly reduce the labeling outcomes.

### Tradeoff in Practice

Approximate Lookup can generalize the matching by considering all sublineages, but at the expense of more computation during lookup.

## Strict Lookup (Full Mapping)

### Data Structure

`mapping.full.json` compiles mapping entries from a full list of commonly known lineages obtained [here](https://github.com/corneliusroemer/pango-sequences). This approach requires no approximate matching; a simple equality lookup on the mapping table keys suffices.

```json
{
    "AY.86": {
        "aliased": "AY.86",
        "nextclade": "21J",
        "unaliased": "B.1.617.2.86",
        "wholabel": "Delta"
    },
    "BN.1.2": {
        "aliased": "BN.1.2",
        "nextclade": "22D",
        "unaliased": "B.1.1.529.2.75.5.1.2",
        "wholabel": "Omicron"
    },
    ...
}
```

The file is generated using `generate_full_mapping.py`. Additional details such as nextstrainClade, aliasing, and unaliasing info are obtained from the above linked dataset.

### Lookup Process

PANGO to WHO mapping in this approach is done by a simple equality match on the lookup keys.

#### Example Lookup Algorithm with JSON
```py
# dictionary created from JSON transformation
mapping = {
    "AY.86": {
        "aliased": "AY.86",
        "nextclade": "21J",
        "unaliased": "B.1.617.2.86",
        "wholabel": "Delta"
    },
    ...
}

def get_wholabel(lineage):
    # check if the lineage is in the mapping dictionary
    if lineage in mapping:
        return mapping[lineage]['wholabel']
    # return Unknown if the lineage is not found
    return "Unknown"
```

You may use approximate lookup on this `.json` file to improve labeling accuracy at the expense of performance.

### Tradeoff in Practice

Strict Lookup offers efficient retrieval but may omit sublineages not included in the predefined definitions.

## How to use?

### Excel Spreadsheet

1. Download `mapping.core.csv`.
2. Copy the data from the `.csv` file into a new worksheet named `mapping` in your Excel file that contains the data to be mapped.
3. Sort data in the `mapping` worksheet in ascending order based on the first column.
4. Assuming the `data` worksheet contains your data with the lineage column, apply the following formula in the `data` worksheet:
    ```
    =IF(ISNUMBER(SEARCH(INDEX(mapping!A:A, MATCH(C2, mapping!A:A, 1)), C2)), INDEX(mapping!B:B, MATCH(C2, mapping!A:A, 1)), "Unknown")
    ```
    Replace `C2` with the cell containing the lineage data.

Refer to `excel_example.xlsx` in the `examples` folder for a practical demonstration.
  
### SQL Database

1. Download `mapping.core.sql` or `mapping.core.csv`.
2. Create an instance of the mapping table in your database by either importing the `.csv` file or running the SQL commands in the `.sql` file. Name this table `mapping`.
3. Assuming the `data` table contains your data with the lineage column, create a new materialised view or table in your database using the following query:
    ```sql
    CREATE TABLE dataview AS
    SELECT 
        a.year, -- data columns from your data table
        a.month, -- data columns from your data table
        COALESCE(a.lineage, 'Unknown') AS ori_lineage, -- lineage colun from your data table
        COALESCE(b.lineage, 'Unknown') AS ref_lineage,
        COALESCE(b.wholabel, 'Unknown')
    FROM 
        data AS a -- your data table
    LEFT JOIN 
        mapping AS b -- mapping table provided by this repo
    ON 
        b.lineage = (
            SELECT 
                lineage
            FROM 
                mapping
            WHERE 
                lineage = ori_lineage -- strict match
                OR ori_lineage LIKE b.lineage || '.%' -- approximate match
            ORDER BY 
                lineage DESC -- most specific match
            LIMIT 1
        );
    ```
    The above query is provided in `examples/maping_query.sql`.

Refer to `sqlite_example.db` in the `examples` folder for a practical demonstration using a SQLite Database.

### Programming (CSV & JSON with Python)

We have provided two sample scripts in the `examples` folder to get you started.

- `get_wholabel_from_csv.py`: Example script using the CSV file with Approximate Lookup. It takes a lineage input and outputs the WHO label. The script uses the `mapping.core.csv` file.

- `get_wholabel_from_json.py`: Example script using the JSON file with Strict Lookup. It takes a lineage input and outputs the WHO label. The script uses the `mapping.full.json` file.

These scripts are ready to run, and you can easily modify them for your specific needs.

## How is the the mapping derived?

You do not have to perform any of the following to do the conversion. The following only gives you an overview on how we derived the conversion / mapping table.

<details>
  <summary>More Details</summary>

The following illustrates how the conversion table is derived:

1. **Base List Creation**:
   - **Source**: Use the base list from the Covariants database (available at [Covariants.org](https://covariants.org/)).
   - **Purpose**: Establish initial mappings of PANGO lineages to WHO labels based on existing data.

2. **Expand and Refine List**:
   - **Sources for Expansion**:
     - GISAID and its resources (e.g., [GISAID](https://gisaid.org/), [GISAIDR GitHub](https://github.com/Wytamma/GISAIDR/blob/master/R/core.R)).
     - WHO updates and variant announcements (e.g., [WHO News](https://www.who.int/news/item/27-10-2022-tag-ve-statement-on-omicron-sublineages-bq.1-and-xbb)).
   - **Example Expansion**:
     - Alpha: `B.1.1.7 / Q.*`
     - Delta: `B.1.617.2 / AY.*`
     - Omicron: `B.1.1.529 / BA.*`
   - **Rules**: Add new alias categories and merge sublineages for better generalization, such as merging `BA.*` and `XBB` under Omicron.

3. **Reference Table Creation**:
   - **Source**: Extract data from PANGO consensus sequences summary available on GitHub ([PANGO Sequences Summary](https://github.com/corneliusroemer/pango-sequences/blob/main/data/pango-consensus-sequences_summary.json)).
   - **Purpose**: Form a reference table (`nextstrain`) for aliasing and unaliasing PANGO lineages.

4. **Unaliasing Lineages**:
   - **SQL Query**:
     ```sql
     SELECT a.lineage,
            a.wholabel,
            GROUP_CONCAT(DISTINCT b.unaliased) AS c
     FROM   covariants AS a
            LEFT JOIN nextstrain AS b
                   ON a.lineage = b.lineage
                    OR b.lineage LIKE a.lineage || '.%'
     GROUP BY a.lineage, a.wholabel
     ORDER BY a.wholabel ASC
     WHERE  c IS NOT NULL AND lineage != c;
     ```
   - **Purpose**: Identify the root lineage of a given lineage from the base list through unaliasing. Identify the most specific common parents of similar sublineages to formulate matching rules with the largest coverage. For example, if `CH.1.1` maps to `B.1.1.529.2.75.3.4.1.1.1.1`, and `B.1.1.529.*` is Omicron, then `CH.*` should be classified as Omicron.

5. **Alias Finding**:
   - **SQL Query**:
     ```sql
     SELECT GROUP_CONCAT(DISTINCT a.lineage),
            GROUP_CONCAT(DISTINCT a.wholabel),
            SUBSTR(b.lineage, 1, INSTR(b.lineage, '.') - 1) AS we,
            GROUP_CONCAT(b.lineage),
            GROUP_CONCAT(DISTINCT b.unaliased)
     FROM   covariants AS a
            LEFT JOIN nextstrain AS b
                   ON unaliased = a.lineage
                    OR unaliased LIKE a.lineage || '.%'
     GROUP BY we
     ORDER BY a.wholabel, we ASC;
     ```
   - **Purpose**: Identify all possible aliases for a given lineage. Focus particularly on Omicron due to its extensive number of sublineages.

6. **New Lineages Identification**:
   - **SQL Query**:
     ```sql
     SELECT we,
            b.lineage
     FROM   (SELECT SUBSTR(lineage, 1, INSTR(lineage, '.') - 1) AS we
             FROM   nextstrain
             WHERE  nextstrainclade LIKE '23_'
                    AND we != ''
             GROUP  BY we) AS a
            LEFT JOIN covariants AS b
                   ON b.lineage = a.we
     WHERE  b.lineage IS NULL;
     ```
   - **Purpose**: Check for new PANGO lineages that may not be present in the base list, focusing on Omicron variants which frequently introduce new lineages.

Manual inspection is involved in each step to ensure accurate generalization and concise addition of new matching rules.

</details>

## Disclaimer

This project is intended for educational purposes only. The creator assumes no responsibility for its use. Users should verify the accuracy of the conversions before applying them to their projects or analyses.
