import csv

mapping = dict()

# get core mapping dataset
# assume the file is in the same directory as this script
with open('mapping.core.csv') as csvfile:
    data = list(csv.reader(csvfile))

# populate mapping dictionary
for i in data:
    mapping[i[0]] = i[1]

# compute wholabel mapping
def get_wholabel(lineage):
    """
    retrieve the WHO label for a given lineage.

    args:
        lineage (str): the lineage to look up.

    returns:
        str or None: the WHO label if found, otherwise None.
    """
    # split with respect to sublineages
    cpn = lineage.split('.')

    # find the longest match
    for i in reversed(range(len(cpn))):
        sub = '.'.join(cpn[:i+1])
        if sub in mapping:
            print(f"matched: {sub}")
            return mapping[sub]
    
    # return None if no matches found
    return None

# iteratively ask for user input
while True:
    try:
        # prompt for user input
        a = input("\nEnter a PANGO lineage: ")
    except KeyboardInterrupt:
        # terminate with Ctrl+C
        print("\nTerminating program.")
        break

    # get wholabel
    b = get_wholabel(a)

    # if no matches found
    if b is None:
        print("No matches found")
        continue
    
    # print results
    print(f"wholabel: {b}")
