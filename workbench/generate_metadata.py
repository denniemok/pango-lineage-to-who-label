import requests
import numpy as np

# get lineage metadata summary
response = requests.get('https://github.com/corneliusroemer/pango-sequences/raw/main/data/pango-consensus-sequences_summary.json')
response.raise_for_status()  # ensure we handle HTTP errors
lineages = response.json()

# populate result set
results = [[x, y['nextstrainClade'], y['unaliased']] for x, y in lineages.items()]

results.insert(0, ['lineage', 'nextclade', 'unaliased'])

# write result set to file
results = np.asarray(results)
np.savetxt("metadata.csv", results, delimiter=",", fmt='%s')
