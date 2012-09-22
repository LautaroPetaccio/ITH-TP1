import os
import subprocess
listaDatos = []

#Devuelve la media muestral de la duracion de los segmentos con habla sobre la cantidad de fonos
def getSpeakTimeMean(ipuList):
	ipuList = filter(lambda x: (x[0] != '') and (x[0] != '#') and (x[0] != '# ') and (x[0] != ' '),ipuList)
	#print ipuList
	return reduce(lambda x, y: x+((y[2]-y[1])/len(y[0])) , ipuList, 0)

def removeFirstSilence(ipuList):
	toDelete = 0
	for segment in ipuList:
		if (segment[0] != '') and (segment[0] != '#') and (segment[0] != '# ') and (segment[0] != ' '):
			break
		else:
			toDelete += 1
	return ipuList[toDelete:]

#Devuelve la media muestral de la duracion de los segmentos sin sonido (sin los silencios al principio ni al final de cada wav)
def getSilenceTimeMean(ipuList):
	#Borro los silencios al principio y al final para que solo queden los silencios entre segmentos
	ipuList = removeFirstSilence(ipuList)
	ipuList.reverse()
	ipuList = removeFirstSilence(ipuList)

	ipuList = filter(lambda x: (x[0] == '') or (x[0] == '#') or (x[0] == '# ') or (x[0] == ' '),ipuList)
	silenceTime = reduce(lambda x, y: x+(y[2]-y[1]) , ipuList, 0)
	return silenceTime/len(ipuList)

#Devuelve la media de F0 de los segmentos que contienen habla del archivo segun el genero, f femenino, m masculino
def getF0Mean(fileName, gender):
	wavFileName = fileName.split(".")[0]+".wav"
	ipuList = filter(lambda x: (x[0] != '') and (x[0] != '#') and (x[0] != '# ') and (x[0] != ' '), getIpuData(fileName))
	FoMean = 0
	invalidData = 0
	for segments in ipuList:
		FData = callPraat(wavFileName, str(segments[1]), str(segments[2]), gender)["F0_MEAN"]
		if FData != "--undefined--":
			FoMean += float(FData)
		else:
			invalidData += 1
	return FoMean/(len(ipuList)-invalidData)

#Llama a praat con el nombre del archivo, el comienzo, el final y el genero, m hombre, f mujer
def callPraat(fileName, begin, end, gender):
	if gender == 'm':
		genderBegin = 70
		genderEnd = 300
	else:
		genderBegin = 100
		genderEnd = 500
	#print "Comando a ejecutar " + "praat acoustics.praat "+fileName+" "+begin+" "+end+" "+str(genderBegin)+" "+str(genderEnd)
	output = subprocess.check_output("praat acoustics.praat "+fileName+" "+begin+" "+end+" "+str(genderBegin)+" "+str(genderEnd), shell=True)
	output = output.split('\n')
	return dict(map(lambda x: x.split(":"), output)[:-1])

#Devuelve los datos de la persona que realizo el test segun el nombre del archivo
def getTestedData(fileName):
	global listaDatos
	name = fileName[:-4].split('-')[0].capitalize()
	subjectName = fileName[:-4].split('-')[1][0]
	testNumber = fileName[:-4].split('-')[1][0]
	gender = ""
	nativeFrom = ""
	age = 0
	for item in listaDatos:
		if item[0] == name and item[1] == subjectName:
			gender = item[2]
			age = int(item[3])
		nativeFrom = item[4]
	return {"name" : name, "subjectName" : subjectName, "gender" : gender, "city" : nativeFrom, "age" : age, "testNumber" : testNumber}

#Devuelve los datos parseados en listas de los ipu, los datos de los .ipu son segmentos, se devuelve una lista de ["texto que se dice", tiempo_inicio, tiempo_termina]
def getIpuData(fileName):
	file = open(fileName, 'r')
	lista = []
	for line in file:
		splittedLine = line.strip('\n').split(' ', 2)
		if len(splittedLine) > 2:
			lista.append([splittedLine[2], float(splittedLine[0]), float(splittedLine[1])])
	file.close()
	return lista

#Carga los datos de data.csv y datos.csv en listaDatos
def loadCSVData():
	file = open("data.csv",'r')
	global listaDatos
	for line in file:
		listaDatos.append(line.replace('"', "").split('	'))
	file.close()
	file = open("datos.csv", 'r')
	for line in file:
		listaDatos.append(line.split(','))
	file.close()


loadCSVData()
print listaDatos

for fileName in os.listdir("."):
	if ".ipu" in fileName:
		print fileName
		print getSilenceTimeMean(getIpuData(fileName))
		#print getF0Mean(fileName, getTestedData(fileName)["gender"])
