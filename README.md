# PANGO Lineage -> WHO Label for COVID-19 Analysis

This project aims to provide a generalised conversion scheme that maps PANGO lineages (like `B.1.1.529` and `AY.2`) to their corresponding WHO labels or names (like `Omicron` and `Delta`).

The ability to swiftly convert between PANGO lineages and WHO labels can streamline data analysis and make COVID-19 statistics more accessible to the general public and non-specialists.

For instance, using our mapping scheme allows for the correct labeling of more than 85% of [GISAID EpiCoV](https://gisaid.org/) records (tested with over 200,000 entries from Australia). The remaining unlabeled records may belong to recombinant lineages, newly identified lineages, lineages not labeled by WHO, or records without a lineage designation.

<h3>Core Mapping List: <a href="https://github.com/denniemok/pango-lineage-to-who-label/blob/main/mapping.core.csv">mapping.core.csv</a> | <a href="https://github.com/denniemok/pango-lineage-to-who-label/blob/main/mapping.core.sql">mapping.core.sql</a> (03Sep24)</h3>

<h3>Full Mapping List: <a href="https://github.com/denniemok/pango-lineage-to-who-label/blob/main/mapping.full.json">mapping.full.json</a> (03Sep24)</h3>

<details>
  <summary>Supported WHO Labels</summary>
  <br>
  Alpha, Beta, Gamma, Delta, Epsilon, Zeta, Eta, Theta, Iota, Kappa, Lambda, Mu, Omicron
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
  <summary>Lineage Aliasing</summary>
  <br>
  Aliasing is the process of finding aliases of a PANGO lineage. This involves identifying the shorter, simplified alias that corresponds to a more complex lineage name in the PANGO system.
  <br><br>
  For example, mapping "B.1.1.529.1" to its shorter alias "BA.1" would be considered alias mapping.
  <br><br>
</details>

## Approximate Lookup (Core Mapping)

### Data Structure

`mapping.core.csv` contains only the **necessary** and **generalised** matching rules. For example, `B.1.1.7 -- Alpha` means both `B.1.1.7` and `B.1.1.7.*` map to Alpha. Sublineages of `B.1.1.7` (i.e., `B.1.1.7.*`) are not explicitly stored in the table to allow the largest descendant coverage in the lookup process.

```sh
+-----------+------------+
|  Lineage  |  wholabel  |
+-----------+------------+
|  AY       |  Delta     | # AY + AY.* -> Delta
|  BB       |  Mu        | # BB + BB.* -> Mu
|  BA       |  Omicron   | # BA + BA.* -> Omicron
|  ...      |  ...       |
+-----------+------------+
```

`mapping.core.sql` provides the same data as `mapping.core.csv` but in the form of SQL statements for replicating the table in a database.

### Lookup Process

PANGO to WHO mapping in this approach is done by approximately matching each record's lineage field in your data with our mapping table. Approximate matching means finding the most specific match.

#### Example Lookup Algorithm
```py
def get_wholabel(lineage):
    # split the lineage by periods to handle hierarchical structure
    cpn = lineage.split('.')
    # iterate over the parts of the lineage in reverse order
    for i in reversed(range(len(cpn))):
        sub = '.'.join(cpn[:i + 1])
        if sub in mapping:
            return mapping.get(sub)
    # return Unknown if no match is found
    return "Unknown"
```

Using only strict lookups on core mapping tables will significantly reduce the labeling outcomes.

### Tradeoff in Practice

Approximate Lookup offers a better labeling coverage by considering all sublineages in matching, but at the expense of more computation during lookup.

## Strict Lookup (Full Mapping)

### Data Structure

`mapping.full.json` compiles mapping entries from a full list of commonly known lineages obtained [here](https://github.com/cov-lineages/lineages-website/blob/master/_data/lineage_data.full.json). This approach requires no approximate matching; a simple equality lookup on the mapping table keys suffices.

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
    }
}
```

The file is generated using `generate_full_mapping.py`. Additional details such as nextstrainClade, aliasing, and unaliasing info are obtained from [this](https://github.com/corneliusroemer/pango-sequences/blob/main/data/pango-consensus-sequences_summary.json) dataset.

### Lookup Process

PANGO to WHO mapping in this approach is done by a simple equality match on the lookup keys.

#### Example Lookup Algorithm
```py
def get_wholabel(lineage):
    # check if the lineage is in the lookup dictionary
    if lineage in mapping:
        return mapping.get(lineage)
    # return Unknown if the lineage is not found
    return "Unknown"
```

You may use approximate lookup on this `.json` file to improve labeling accuracy at the expense of performance.

### Tradeoff in Practice

Strict Lookup offers efficient retrieval but may omit sublineages or ancestors not included in the predefined definitions.

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

Refer to `excel_example.xlsx` in the `example` folder for a practical demonstration.
  
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
                OR ori_lineage LIKE lineage || '.%' -- approximate match
            ORDER BY 
                lineage DESC -- most specific match
            LIMIT 1
        );
    ```
    The above query is provided in `example/maping_query.sql`.

Refer to `sqlite_example.db` in the `example` folder for a practical demonstration using a SQLite Database.

### Programming (CSV & JSON with Python)

We have provided two sample scripts in the `example` folder to get you started.

- `get_wholabel_from_csv.py`: Example script using the CSV file with Approximate Lookup. It takes a lineage input and outputs the WHO label. The script uses the `mapping.core.csv` file.

- `get_wholabel_from_json.py`: Example script using the JSON file with Strict Lookup. It takes a lineage input and outputs the WHO label. The script uses the `mapping.full.json` file.

These scripts are ready to run, and you can easily modify them for your specific needs.

## How is the the mapping derived?

You do not have to perform any of the following to do the conversion. The following only gives you an overview on how we derived the conversion / mapping table.

<details>
  <summary>More Details</summary>

1. **Base List Creation**:
   - **Source**: Utilise definitions from [CoVariants](https://covariants.org/) and [Wikipedia](https://en.wikipedia.org/wiki/Variants_of_SARS-CoV-2).
   - **Purpose**: Establish initial mappings of PANGO lineages to WHO labels based on consensus data.

2. **Base List Refinement**:
   - **Sources for Expansion**:
     - [GISAID]([https://gisaid.org/](https://gisaid.org/hcov19-variants/))
     - [GISAIDR](https://github.com/Wytamma/GISAIDR/blob/master/R/core.R)
     - [WHO News](https://www.who.int/news/item/27-10-2022-tag-ve-statement-on-omicron-sublineages-bq.1-and-xbb)
   - **Example Expansion**:
     - Alpha: `B.1.1.7 = Q`
     - Delta: `B.1.617.2 = AY`
     - Omicron: `B.1.1.529 = BA`
   - **Purpose**: Add direct aliases to the base list and merge sublineages into their common ancestors for better coverage, such as combining all `BA` and `XBB` sublineages into their respective categories.

3. **Reference Table Creation**:
   - **Source**: Extract data from [PANGO Consensus Sequences Summary](https://github.com/corneliusroemer/pango-sequences/blob/main/data/pango-consensus-sequences_summary.json) and [PANGO Designation Alias Key](https://github.com/cov-lineages/pango-designation/blob/master/pango_designation/alias_key.json) available on GitHub.
   - **Purpose**: Form the reference table `metadata` for aliasing and unaliasing PANGO lineages.

4. **Lineage Unaliasing**:
   - **SQL Query**:
     ```sql
     SELECT * FROM (
     SELECT a.lineage,
            a.wholabel,
            GROUP_CONCAT(DISTINCT b.unaliased) AS c
     FROM   mapping AS a
            LEFT JOIN metadata AS b
                   ON a.lineage = b.lineage
                    OR b.lineage LIKE a.lineage || '.%'
     GROUP BY a.lineage, a.wholabel
     ORDER BY a.wholabel ASC
     ) WHERE  c IS NOT NULL AND lineage != c;
     ```
   - **Purpose**: Identify the root lineage of a given lineage from the base list through unaliasing. Determine the most specific common ancestors of similar sublineages to formulate matching rules with broadder coverage. For example, if `CH.1.1` maps to `B.1.1.529.2.75.3.4.1.1.1.1`, and `B.1.1.529.*` is Omicron, then `CH.*` should be classified as Omicron.

5. **Lineage Aliasing**:
   - **SQL Query**:
     ```sql
     SELECT GROUP_CONCAT(DISTINCT a.lineage),
            GROUP_CONCAT(DISTINCT a.wholabel),
            SUBSTR(b.lineage, 1, INSTR(b.lineage, '.') - 1) AS plin,
            GROUP_CONCAT(b.lineage),
            GROUP_CONCAT(DISTINCT b.unaliased)
     FROM   mapping AS a
            LEFT JOIN metadata AS b
                   ON unaliased = a.lineage
                    OR unaliased LIKE a.lineage || '.%'
     GROUP BY plin
     ORDER BY a.wholabel, plin ASC;
     ```
   - **Purpose**: Identify all possible aliases for a given lineage, with a particular focus on Omicron due to its numerous sublineages and descendants.

6. **Cross-Checking**:
   - **SQL Query**:
     ```sql
     WITH lineage_cte AS (
         SELECT SUBSTR(lineage, 1, INSTR(lineage, '.') - 1) AS plin,
                nextclade
         FROM metadata
         WHERE nextclade LIKE '23_' AND plin != ''
         GROUP BY plin, nextclade
     )
     SELECT plin,
            nextclade,
            b.lineage
     FROM lineage_cte AS a
     LEFT JOIN mapping AS b
         ON b.lineage = a.plin
     WHERE b.lineage IS NULL;
     ```
   - **Purpose**: Identify lineages that may be missing from the list but should be labeled according to the Nextstrain Clade consensus (e.g., `23I` mapping to `Omicron`) using data from [CoVariants](https://covariants.org/). Pay special attention to Omicron, given its frequent emergence of new recombinant lineages.

Manual inspection is involved at each step to ensure accurate generalisation and concise addition of new matching rules.

The file `mapping.core.csv` represents the final output of the process described above. The `generate_full_mapping.py` script is then executed to produce `mapping.full.json`, which includes more detailed information for direct lookup.

</details>

## Disclaimer

This project is intended for educational purposes only. The creator assumes no responsibility for its use. Users should verify the accuracy of the conversions before applying them to their projects or analyses.
