# Converts dlv output to dot
# __author__ = "Parisa Kianmajd"
#__version__ = "1.0.1"

import subprocess
import sys

def addDict(label, e, d):
    if label not in d:
        d.update({label:list()})
    d[label].append(e)
                 
nodes = dict() 
edges = list()
custom = dict()
publish = list()  # list of nodes that have to be published and their lineage
covered = list()
abstract = dict()
rules = list()

command = 'dlv -silent '
for a in sys.argv[1:]:
   command += a + " "
proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
lst = out.strip().split('\n')
for d in lst:
    rules.append(d[d.find("{")+1:d.find("}")].split(", "))
for rule in rules:
        for r in rule:
            if ',' in r:
                half = r.split(',')
                second = half[0].split('(')
                label = second[0]
                start = second[1]
                end = half[1][:-1]
                if label in ['actor','data', 'l_actor','l_data']:
                 addDict(label, (start,end), nodes)
                elif label in ['used', 'gen_by']:
                        edges.append((start,end,label))
                else:
                 addDict(label, (start,end), custom)  
            else:
                label = r.split("(")[0]
                start = r[r.find("(")+1:r.find(")")]
                addDict(label, start, custom)
if 'lineage' in custom:
    for r in custom['lineage']:
        publish.append(r)
if 'l_dep' in custom:
    for r in custom['l_dep']:
        if r[0] in publish:
            publish.append(r[1])

output = outputa= outputc ='digraph{\n rankdir = RL \n'
for n in nodes:
    if n in ['data','actor']:
        if n == 'data':
            outputa += 'node[shape = circle]\n'
            output += 'node[shape = circle]\n'
        elif n == 'actor':
            outputa += 'node[shape = box]\n'
            output += 'node[shape = box]\n'
        if n in ['data', 'actor']:
            for node in nodes[n]:
                outputa += str(node[0]) + '\n'
                if node[0] in publish:
                    output += str(node[0]) + '\n'
for n in nodes:
    if n in ['l_data','l_actor']:
        if n == 'l_data':
            outputc += 'node[shape = circle]\n'
        elif n == 'l_actor':
            outputc += 'node[shape = box]\n'
        for node in nodes[n]:
            if node[0] not in custom['anonymize']:  # the anonymized nodes are seperated as they have a different style
                outputc += str(node[0]) + '\n'
                
style = 'style=dashed penwidth = 2 fontcolor = "#197319" color = "#197319"'
if 'abstract' in custom:
    for c in custom['abstract']:
                     addDict(c[1],c[0],abstract)
for a in abstract:
    outputc += 'node[shape = box]\n'
    outputc += str(a) + '\n'
    output += 'subgraph cluster' + str(a) + ' { ' + style + 'label = abstract\n'
    for node in abstract[a]:
        output += str(node) + '\n'
if len(abstract) != 0:
    output += '}\n'

for e in edges:
    if e[2] == 'used':
        if e[1] in custom['hide_node'] and e[0] not in custom['hide_node']:
            if e[0] in nodes['data']:
                outputc += 'node[shape=box]\n'
            else:
                outputc += 'node[shape=circle]\n'
            outputc += str(e[0]) +'\n'
if 'anonymize' in custom:
    outputc += 'node[shape = circle style = "filled, dotted" fillcolor = "#e0e0e0"]\n'
    for n in custom['anonymize']:
                outputc += str(n) + '\n'

edgestyle = 'edge[style = dashed color = blue]\n'            
output += edgestyle
outputa += edgestyle

for e in edges:
    outputa += str(e[0]) + ' -> ' + str(e[1]) + '\n'
    if e[0] in publish and e[0] in publish:
        output += str(e[0]) + ' -> ' + str(e[1]) + '\n'
    if (e[0],e[1]) in custom['l_dep_new']:
        outputc += edgestyle
        outputc += str(e[0]) + ' -> ' + str(e[1]) + '\n'

for rule in custom:
    if rule == 'hide_edge':
        for r in custom[rule]:
            output += 'subgraph cluster' + str(r[0]) + ' { ' + style + ' label = hide\n'
            for c in r:
                covered.append(c)
                output += str(c) + '\n'
            output += '} \n'
    elif rule == 'hide_node':
        for c in custom[rule]:
            if c not in covered:
                output += 'subgraph cluster' + str(c) + ' { ' + style + ' label= hide\n'
                output += str(c) + '\n }\n'
    elif rule == 'abstract':
        for c in custom[rule]:
            addDict(c[1],c[0],abstract)
    elif rule == 'anonymize':
        output += 'subgraph cluster' + custom[rule][0] + ' { ' + style + 'label= anonymize\n'
        for c in custom[rule]:
            output += str(c) + '\n'
        output += '}\n'
    elif rule == 'lineage':
        for c in custom[rule]:
            outputa += 'subgraph cluster' + str(c) + ' { ' + 'style=dashed penwidth = 2 fontcolor = blue color = blue label= lineage\n'
            outputa += str(c) + '\n'
            outputa += '}\n'
    elif rule == 'l_dep_new':
        outputc += 'edge[style=dashed color = "#197319"]\n'
        for c in custom[rule]:
            if (c[0],c[1]) not in [(e[0],e[1]) for e in edges]:
                outputc += str(c[0]) + ' -> ' + str(c[1]) + '\n'

output += '} \n'
outputa += '} \n'
outputc += '} \n'
output += "}"

f = open('outb.dot',"w")
f.write(output)
f.close()
f = open('outa.dot',"w")
f.write(outputa)
f.close()
f = open('outc.dot',"w")
f.write(outputc)
f.close()
              
                        
        
        
    
