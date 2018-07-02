from flask import Flask, url_for
from flask import request
import requests
import json
from time import sleep

#criar uma lista ou contador de workers conectados para troca de informação baseado na porta
dados = None

app = Flask(__name__)

listaWorkers = []
dicionarioWorkers = {}

def setarComoTrabalhandoUmTrabalhador(ip):
    for worker in listaWorkers:
        if (worker['ipTrabalhador'] == str(ip)):
            worker['busy'] = 'True'

def setarComoLivreUmTrabalhador(ip):
    for worker in listaWorkers:
        if (worker['ipTrabalhador'] == str(ip)):
            worker['busy'] = 'False'

def balancear(cpu, mem):

    qtdTrabalhadores = len(listaWorkers)

    if (qtdTrabalhadores > 0):
        listaControle = []

        for worker in listaWorkers:
            print (worker, 'TRABALHADOR -----------------')
            if (worker['busy'] == 'False'):
                listaControle.append(worker)
            
        if (len(listaControle)>0):

            listaTrabalhadoresQueSuportam = []

            for worker in listaControle:
                if (int(worker['CPUs']) >= int(cpu) and int(worker['MemTotal']) >= int(mem)):
                    listaTrabalhadoresQueSuportam.append(worker)

            if (len(listaTrabalhadoresQueSuportam) > 0):
                maior = '0'
                for workerSuporta in listaTrabalhadoresQueSuportam:
                    if (int(workerSuporta['Score']) > int(maior) ):
                        maior = workerSuporta['Score']

                for worker in listaTrabalhadoresQueSuportam:
                    if (worker['Score'] == maior):
                        setarComoTrabalhandoUmTrabalhador(worker['ipTrabalhador'])
                        return worker['ipTrabalhador']                          

    else: 
        return 'Não há trabalhadores no momento!'

@app.route('/capturarInformacoesWorker', methods=['POST'])
def capturarInformacoesWorker():

    ip = request.remote_addr
    dicIP = {}
    dicIP['ipTrabalhador'] = ip
    
    data = request.get_json()
    data = json.loads(data)

    tempValor = {}
    if ('GeForce GTX 780' in data['Product Name']):
        tempValor['Score'] = 500
    elif ('TITAN X (Pascal)' in data['Product Name']):
        tempValor['Score'] = 800
    elif ('GeForce GTX 1070' in data['Product Name']):
        tempValor['Score'] = 700

    data.update(tempValor)
    data.update(dicIP)

    listaWorkers.append(data)

    print (listaWorkers, '---LISTA---')

    return 'Sucesso'


@app.route('/verificarMiddleware', methods=['GET'])
def verificarMiddleware():
    retorno = {}
    if request.method == 'GET':
        ip = request.remote_addr
        dicionarioWorkers['ipTrabalha   dor'] = ip   
        retorno['Message'] = 'Method allowed'
    else:
        retorno['Message'] = 'Method not allowed'

    #print (dicionarioWorkers)
    
    return json.dumps(retorno)

@app.route('/receberDadosCliente', methods=['POST'])
def recebeDados():
    if request.method == 'POST':
        data = request.get_json()
        print (data, '<----')
        data = json.loads(data)
        print (len(data))
        retorno = {}
        if data:
            ip = balancear(data['cpu'], data['memoria'])
            retorno['ip'] = ip
            print (ip)
        
            treinar = requests.post('http://' + ip + ':5001/treinar', json = json.dumps(data))

            print (treinar.json())

            setarComoLivreUmTrabalhador(ip)
            print (dicionarioWorkers)
            return json.dumps(retorno)
        else:
            retorno['Message'] = 'Without data'
            return json.dumps(retorno)
    else:
        retorno = {}
        retorno['Message'] = 'Method not allowed'
        return json.dumps(retorno)

@app.route('/mostrarDados', methods=['GET'])
def enviarDados():
    if request.method == 'GET':
        return 'Method allowed'
    else:
        return 'Method not allowed'

if __name__ == "__main__":
    app.run(host='172.16.1.118', port=5000)

    #sleep(5)
