import os

def extractText(source, target, nonpadded):
    os.system(' '.join(["pdftotext -layout", source, nonpadded]))
    ''' padding '''
    linesFinal = []
    with open(nonpadded, 'r') as reader:
        lines = reader.readlines()
        lines.insert(0,"\n")
        maxLen = len(max(lines, key=len))
        for line in lines:
            linesFinal.append(line.replace('\n','').ljust(maxLen))

    with open(target, mode= 'wt', encoding= 'utf-8') as myFile:
        myFile.write('\n'.join(linesFinal))
