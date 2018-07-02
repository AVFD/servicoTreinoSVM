#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, url_for
from flask import request
import json
import subprocess

app = Flask(__name__)

@app.route('/processarDados', methods=['POST'])
def recebeDados():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            dados = data
            return 'Dado recebido'
        else:
            return 'Dado não recebido'
    else:
        return 'Método indisponivel nessa rota'

@app.route('/mostrarDados', methods=['GET'])
def enviarDados():
    if request.method == 'GET':
        a = subprocess.check_output(['nvidia-smi', '-q'])
        a = str(a).split('\n')
        dicionarioRetorno = {}
        for linha in range (0, len(a)):
            if ('Product Name' in a[linha] or 'Fan Speed' in a[linha] or 'FB Memory Usage' in a[linha] or 'GPU Current Temp' in a[linha]):
                if ('FB Memory Usage' in a[linha]):
                    for j in range (1, 4):
                        repartido = a[linha+j].split(':')
                        repartido[0] = repartido[0].strip()
                        dicionarioRetorno[repartido[0]] = repartido[1]
                else:
                    print (a[linha])
                    repartido = a[linha].split(':')
                    repartido[0] = repartido[0].strip()
                    dicionarioRetorno[repartido[0]] = repartido[1]


        print (dicionarioRetorno)       
        return json.dumps(dicionarioRetorno)
    else:
        return 'Método indisponivel nessa rota'

if __name__ == "__main__":
    #porta = 5000

    #fazer request para organizar a porta do servidor... 

    app.run(host='172.16.3.10', port=5001)  