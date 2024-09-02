import requests
import json
import csv

# get lineage metadata summary
response = requests.get('https://github.com/corneliusroemer/pango-sequences/raw/main/data/pango-consensus-sequences_summary.json')
response.raise_for_status()  # ensure we handle HTTP errors
lineages = response.json()

# initialise dictionaries
results = dict()
mapping = dict()

# compute wholabel mapping
def get_wholabel(lineage):
    """
    retrieve the WHO label for a given lineage.

    args:
        lineage (str): The lineage to look up.

    returns:
        str: The WHO label if found, otherwise 'Unknown'.
    """
    # split with respect to sublineages
    cpn = lineage.split('.')

    # find the longest match
    for i in reversed(range(len(cpn))):
        sub = '.'.join(cpn[:i+1])
        if sub in mapping:
            return mapping[sub]
    
    # return 'Unknown' if no matches found
    return 'Unknown'

# load core mapping dataset
with open('mapping.core.csv') as csvfile:
    data = list(csv.reader(csvfile))

# populate mapping dictionary
for i in data:
    mapping[i[0]] = i[1]

# populate result set
for x, y in lineages.items():
    results[x] = {
        'nextclade': y['nextstrainClade'],
        'wholabel': get_wholabel(x),
        'unaliased': y['unaliased'],
        'aliased': x
    }

    z = y['unaliased'] 

    # put unaliased entries as separate entries to facilitate searching
    if z not in results:
        results[z] = {
            'nextclade': y['nextstrainClade'],
            'wholabel': get_wholabel(z),
            'unaliased': y['unaliased'],
            'aliased': x
        }

# write result set to file
with open('mapping.full.json', 'w') as fp:
    json.dump(results, fp, indent=4, sort_keys=True)
