import requests
# import json  # uncomment if using local file instead of online

# fetch full mapping dataset online
response = requests.get('https://github.com/denniemok/pango-lineage-to-who-label/raw/main/mapping.full.json')
response.raise_for_status()  # ensure we catch HTTP errors
mapping = response.json()

# fetch full mapping dataset locally (alternative method)
# assume the file is in the same directory as this script
# with open('mapping.full.json') as jsonfile:
#     mapping = json.load(jsonfile)

def get_wholabel(lineage):
    """
    retrieve the WHO label information for a given lineage.

    args:
        lineage (str): the lineage to look up.

    returns:
        dict or None: a dictionary with WHO label information if found, otherwise None.
    """
    return mapping.get(lineage)

# iteratively ask for user input
while True:
    try:
        # prompt for user input
        a = input("\nEnter a PANGO lineage: ")
    except KeyboardInterrupt:
        # handle termination with Ctrl+C
        print("\nTerminating program.")
        break

    # get WHO label information
    b = get_wholabel(a)

    # if no match is found, notify the user
    if b is None:
        print("No matches found")
        continue
    
    # print results
    print(f"WHO label: {b['wholabel']}")
    print(f"Nextclade: {b['nextclade']}")
    print(f"Unaliased: {b['unaliased']}")
    print(f"Aliased: {b['aliased']}")
