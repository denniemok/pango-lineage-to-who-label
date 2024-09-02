import requests
# import json


# get full mapping dataset online
response = requests.get('https://github.com/denniemok/pango-lineage-to-who-label/raw/main/mapping.full.json')
response.raise_for_status()
mapping = response.json()


# get full mapping dataset locally
# with open('mapping.full.json') as jsonfile:
#     mapping = json.load(jsonfile)


# compute wholabel mapping
def get_wholabel(lineage):
    if lineage in mapping:
        return mapping[lineage]
    return None


# iteratively ask for user input
while True:

    try: # prompt for user input
        a = input("\nEnter a PANGO lineage: ")
    except KeyboardInterrupt: # terminate with Ctrl+C
        break

    # get wholabel
    b = get_wholabel(a)

    # if no matches found
    if b is None:
        print("No matches found")
        continue
    
    # print results
    print(f"wholabel: {b['wholabel']}")
    print(f"nextclade: {b['nextclade']}")
    print(f"unaliased: {b['unaliased']}")
    print(f"aliased: {b['aliased']}")