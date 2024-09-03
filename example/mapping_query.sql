CREATE TABLE dataview AS
SELECT 
    a.year, -- data columns from your data table
    a.month, -- data columns from your data table
    COALESCE(a.lineage, 'Unknown') AS ori_lineage, -- lineage column from your data table
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