CREATE TABLE dataview AS
SELECT 
    a.year,
    a.month,
    COALESCE(a.lineage, 'Unknown') AS ori_lineage,
    COALESCE(b.lineage, 'Unknown') AS ref_lineage,
    COALESCE(b.wholabel, 'Unknown')
FROM 
    data AS a
LEFT JOIN 
    mapping AS b
ON 
    ori_lineage = b.lineage
    OR ori_lineage LIKE b.lineage || '.%'
ORDER BY 
    a.year ASC, 
    a.month ASC;