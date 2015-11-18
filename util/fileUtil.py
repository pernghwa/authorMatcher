import csv

def generate_csv(fname,skip=False):
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        count = 0
        for row in reader:
            if count == 0:
                count += 1
                continue
            yield row
