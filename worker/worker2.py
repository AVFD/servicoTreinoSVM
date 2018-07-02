#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
import requests
import json
import subprocess
import multiprocessing
import os

app = Flask(__name__)

def treinarSVM(mem, cpu):
    try:
        #saidaProcesso = subprocess.check_output(['python', '/home/joao/servico/loop.py'])
        saidaProcesso = subprocess.check_output(['/home/joao/servico/thunderSVM/thundersvm/build/bin/thundersvm-train', '-c', '100', '-b', '1', '-o', str(cpu), '-u', '0', '-m', str(mem), '/home/joao/servico/datasets/test_features_exballroom-ds_linspace-fs_40-nfeats_1-f_libsvm.txt', 'modelSamll'])
        #os.system('./bin/thundersvm-train -c 100 -b 1 -u 0 -m ' + str(mem) + '-o ' + str(cpu) +  '/home/joao/servico/thunderSVM/thundersvm/dataset/test_dataset.txt')
        print ('sucesso')
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print ('sem sucesso')
        
        
@app.route('/treinar', methods=['POST'])
def treinar():
    if request.method == 'POST':
        data = request.get_json()
        data = json.loads(data)
        print (data)
        mem = data['memoria'].encode("ascii","replace")
        cpu = data['cpu'].encode("ascii","replace")

        print (mem, cpu, '<-- CPU/MeM')

        processoTreino = multiprocessing.Process(target=treinarSVM(int(mem), int(cpu)))
        processoTreino.start()

        retorno = {}
        retorno['Message'] = 'Accepted'
        return json.dumps(retorno)
    else:
        retorno = {}
        retorno['Message'] = 'Method not allowed'
        return json.dumps(retorno)
    

def checarConexaoMiddleware():
    retornoPing = subprocess.check_output(['ping', '-c 4', '172.16.3.5'])
    retornoPing = str(retornoPing).split('\n')

    cont = 0
    for linha in retornoPing:
        if ('from' in linha and 'icmp_seq' in linha):
            cont += 1

    if (cont > 0):
        try:
            retornoMid = (requests.get('http://172.16.3.5:5000/verificarMiddleware')).json()
            if (retornoMid and not 'not' in retornoMid['Message']):
                return True
            else:
                return False
        except:
            return False

    else:
        return False


def coletarDadosPC():
    saidaProcesso = subprocess.check_output(['nvidia-smi', '-q'])
    saidaProcesso = str(saidaProcesso).split('\n')
    dicionarioRetorno = {}
    for linha in range (0, len(saidaProcesso)):
        if ('Product Name' in saidaProcesso[linha] or 'Fan Speed' in saidaProcesso[linha] or 'FB Memory Usage' in saidaProcesso[linha] or 'GPU Current Temp' in saidaProcesso[linha]):
            if ('FB Memory Usage' in saidaProcesso[linha]):
                for j in range (1, 4):
                    repartido = saidaProcesso[linha+j].split(':')
                    repartido[0] = repartido[0].strip()
                    dicionarioRetorno[repartido[0]] = (repartido[1].split(' MiB'))[0]
            else:
                repartido = saidaProcesso[linha].split(':')
                repartido[0] = repartido[0].strip()
                if ('Fan Speed' in saidaProcesso[linha]):
                    dicionarioRetorno[repartido[0]] = (repartido[1].split('%'))[0]
                elif ('GPU Current Temp' in saidaProcesso[linha]):
                    dicionarioRetorno[repartido[0]] = (repartido[1].split('C'))[0]
                else:
                    dicionarioRetorno[repartido[0]] = repartido[1]
                

    #print (dicionarioRetorno)     
    
    saidaProcesso = subprocess.check_output(['grep', '-c', '^processor', '/proc/cpuinfo'])
    saidaProcesso = (saidaProcesso.split('\n'))[0]
    dicionarioRetorno['CPUs'] = saidaProcesso

    usoCPU = subprocess.check_output(['uptime'])

    usoCPU = str(usoCPU).split(': ')
    usoCPU = usoCPU[1].split(', ')
    usoCPU = usoCPU[2]
    usoCPU = (usoCPU.split('\n'))[0]

    dicionarioRetorno['usoCPU'] = usoCPU

    totalRam = subprocess.check_output(['cat', '/proc/meminfo'])
    totalRam = (totalRam.split('\n'))[0]
    totalRam = totalRam.split(':')
    totalRam[1] = totalRam[1].strip()
    totalRam[1] = totalRam[1].replace('kB', '')

    calculo = (int(totalRam[1]))/1024 #converte para Mb

    if (calculo > 1):
        totalRam[1] = str(calculo)

    print (totalRam)

    dicionarioRetorno['busy'] = 'False'

    dicionarioRetorno[totalRam[0]] = totalRam[1]

    #print (dicionarioRetorno)
      
    #return json.dumps(dicionarioRetorno)
    return dicionarioRetorno

def enviarDados():

    dicDados = coletarDadosPC()
    print (dicDados)

    retorno = requests.post('http://172.16.3.5:5000/capturarInformacoesWorker', json=json.dumps(dicDados))
    print (retorno.text)



if __name__ == "__main__":
    #treinarSVM(1024, 1)
    #coletarDadosPC()
    if (checarConexaoMiddleware()):
        enviarDados()
        app.run(host='172.16.3.11', port=5001)  

    else:
        print ("Sorry, but can't connect to Middleware")
