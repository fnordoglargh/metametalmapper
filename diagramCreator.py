

def prepareGraph(bandToBandsDict):
    graph = []
    graph.append("strict graph Metal\n{\n\tedge [len=4];\n")
    for k, v in bandToBandsDict.items():
        for bandName in v:
            graph.append('\t"')
            graph.append(k)
            #graph.append(k.encode('utf-8'))
            graph.append('" -- "')
            #graph.append(bandName.encode('utf-8'))
            print(bandName)
            graph.append(bandName)
            graph.append('";\n')
    graph.append('}')

    return ''.join(graph)

def writeGraphAndCallGraphviz(graphvizString):
    bandsFile = open('bandsGraph.dot', 'w')
    #bandsFile.write(graphvizString.encode('utf-8'))
    bandsFile.write(graphvizString)
    bandsFile.close()
    #os.system("fdp -Tpng bandsGraph.dot -o bandsGraph.png")
