RATIO = 95

f = open("data/new_lexique.csv", "r")
l = f.read()
f.close()

l = l.split("\n")
for r in l[:37]:
    print(r)

k = []
for r in l[37:]:
    if r != '':
        rr = r.split('|')
        k.append(float(rr[-1]))
import numpy as np

quant = np.percentile(k,RATIO)
selected = []
for r in l[37:]:
    if r != '':
        if float(r.split('|')[-1]) >= quant:
            selected.append(r)

print(quant)
print(len(l[37:]),len(selected))
print(sorted(selected,key=lambda x: 0 if x == '' else float(x.split('|')[-1]),reverse=True)[0])
print(sorted(selected,key=lambda x: 0 if x == '' else float(x.split('|')[-1]),reverse=True)[-1])

f = open("data/new_lexique_elag.csv", "w")
for r in l[:37]:
    f.write(r)
    f.write("\n")
for r in selected:
    f.write(r)
    f.write("\n")
f.close()