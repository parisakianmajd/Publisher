# f2d converts dlv output to dot
# The code is aware of the states and generate a seperate output for each state in the process
# __author__ = "Parisa Kianmajd"
#__version__ = "1.0.1"

import subprocess
import sys

def addDict(label, e, d):
    if label not in d:
        d.update({label:list()})
    d[label].append(e)

def w2f(text, filename):
    f = open(filename, "w")
    f.write(text)
    f.close()

def addSubgraph(group, label,output):
    for g in group:
        output += 'subgraph cluster' + str(g[0]) + str(g[1]) + ' { ' + style + ' color = red fontcolor = red label= "' + str(label) + '" \n'
        output += str(g[0]) + '\n' +  str(g[1]) + '}\n'
    return output
                 
nodes = dict() 
edges = list()
custom = dict()
rules = list()
pRules = dict()
publish = list()  # list of nodes that have to be published and their lineage
covered = list()
abstract = dict()

ruleName = {'nc':'Cycle', 'nfs': 'Structural Conflict', 'wc': 'Write Conflict', 'nfs': 'False Independance'}

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
                label = r.split("(")[0]
                rlst = r[r.find("(")+1:r.find(")")].split(',')
                if label in ['lineage','anonymize','hide_node','hide_edge','abstract']:
                    addDict(label, (rlst[0], rlst[1]), pRules)
                elif label in ['actor','data']:
                     addDict(label, rlst[0], nodes)
                elif label in ['used', 'gen_by']:
                        edges.append((rlst[0],rlst[1],label))
                elif label not in ['smaller', 'next', 'same_group', 'minimum','next']:
                    if int(rlst[2]) not in custom:
                        custom.update({int(rlst[2]):dict()})
                    if label not in custom[int(rlst[2])]:
                        custom[int(rlst[2])].update({label:list()})
                    custom[int(rlst[2])][label].append((rlst[0], rlst[1]))
            else:
                label = r.split("(")[0]
                addDict(label,r[:-1].split("(")[1],pRules)

if 'lineage' in pRules:
    for r in pRules['lineage']:
        publish.append(r)
for r in custom[0]['l_dep']:
    if r[0] in publish:
        publish.append(r[1])
output = outputa ='digraph{\n rankdir = RL \n'
for n in nodes:
    if n == 'data':
        outputa += 'node[shape = circle]\n'
        output += 'node[shape = circle]\n'
    elif n == 'actor':
        outputa += 'node[shape = box]\n'
        output += 'node[shape = box]\n'
    for node in nodes[n]:
        outputa += str(node) + '\n'
        if node in publish:
            output += str(node) + '\n'

style = 'style=dashed penwidth = 2 fontcolor = "#197319" color = "#197319"'
if 'abstract' in pRules:
    for c in pRules['abstract']:
                     addDict(c[1],c[0],abstract)
for a in abstract:
    output += 'subgraph cluster' + str(a) + ' { ' + style + 'label = abstract\n'
    for node in abstract[a]:
        output += str(node) + '\n'
if len(abstract) != 0:
    output += '}\n'

edgestyle = 'edge[style = dashed color = blue]\n'            
output += edgestyle
outputa += edgestyle

for e in edges:
    outputa += str(e[0]) + ' -> ' + str(e[1]) + '\n'
    if e[0] in publish and e[0] in publish:
        output += str(e[0]) + ' -> ' + str(e[1]) + '\n'
for rule in pRules:
    if rule == 'hide_edge':
        for r in pRules[rule]:
            output += 'subgraph cluster' + str(r[0]) + ' { ' + style + ' label = hide\n'
            for c in r:
                covered.append(c)
                output += str(c) + '\n'
            output += '} \n'
    elif rule == 'hide_node':
        for c in pRules[rule]:
            if c not in covered:
                output += 'subgraph cluster' + str(c) + ' { ' + style + ' label= hide\n'
                output += str(c) + '\n }\n'
    elif rule == 'abstract':
        for c in pRules[rule]:
            addDict(c[1],c[0],abstract)
    elif rule == 'anonymize':
        output += 'subgraph cluster' + pRules[rule][0] + ' { ' + style + 'label= anonymize\n'
        for c in pRules[rule]:
            output += str(c) + '\n'
        output += '}\n'
    elif rule == 'lineage':
        for c in pRules[rule]:
            outputa += 'subgraph cluster' + str(c) + ' { ' + 'style=dashed penwidth = 2 fontcolor = blue color = blue label= lineage\n'
            outputa += str(c) + '\n'
            outputa += '}\n'

output += '} \n'
outputa += '} \n'
output += "}"

w2f(output, 'outb.dot')
w2f(outputa, 'outa.dot')

outputc = [0] * (int(pRules['final'][0]) + 1)
temp = ""
edges2 = list()
for e in edges:
    edges2.append((e[0],e[1]))
abst = set()
for s in custom:
    ncSub = list()
    outputc[s] = 'digraph{\n rankdir = RL \n'
    for label in custom[s]:
        if label in ['l_data','l_actor']:
            if label == 'l_data':
                outputc[s] += 'node[shape = circle]\n'
            elif label == 'l_actor':
                outputc[s] += 'node[shape = box]\n'
            for node in custom[s][label]:
                if node[0] not in pRules['anonymize']:  # the anonymized nodes are seperated as they have a different style
                    outputc[s] += str(node[0]) + '\n'
    if s >= 1:
        if 's_abstract' in custom[s-1]:
            for c in custom[s-1]['s_abstract']:
                abst.add(c[1])
            for a in abst:
                outputc[s] += 'node[shape = box]\n'
                outputc[s] += str(a) + '\n'
    if 'del_dep' in custom[s]:
        for ed in custom[s]['del_dep']:
            if ed[1] in pRules['hide_node'] and ed[0] not in pRules['hide_node']:
                if ed[0] in nodes['data']:
                    temp += 'node[shape=circle]\n'
                else:
                    temp += 'node[shape=box]\n'
                temp += str(ed[0]) +'\n'
                for a in custom[s]['del_dep']:
                    if a[0] == ed[1]:
                        temp += str(ed[0]) + ' -> ' + a[1] + ' [style = invisible arrowhead = none]\n'
                        break
    if temp!= "" and s!= 0:
        outputc[s] += temp
    if 'anonymize' in pRules:
        outputc[s] += 'node[shape = circle style = "filled, dotted" fillcolor = "#e0e0e0"]\n'
        for n in pRules['anonymize']:
                    outputc[s] += str(n) + '\n'
    if 'nc' in custom[s]:
        for c in custom[s]['nc']:
            if (c[1],c[0]) not in ncSub:
                ncSub.append((c[0],c[1]))
        outputc[s] = addSubgraph(ncSub, ruleName['nc'], outputc[s])
    for rule in ['wc','nfs']:
        if rule in custom[s]:
            outputc[s]= addSubgraph(custom[s][rule], ruleName[rule], outputc[s])
    
            
    outputc[s] += 'edge[style = dashed color = blue]\n' 
    for e in custom[s]['l_dep']:
        if e in edges2:
            outputc[s] += str(e[0]) + ' -> ' + str(e[1]) + '\n'
    outputc[s] += 'edge[style = dashed color = "#197319"]\n' 
    for e in custom[s]['l_dep']:
        if e not in edges2:
            outputc[s] += str(e[0]) + ' -> ' + str(e[1]) + '\n'
    outputc[s] += '} \n'
    w2f(outputc[s], 'outc' + str(s) + '.dot')
