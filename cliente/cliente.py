import requests
import json
import os
import subprocess

def enviarDadosMid(dados):

    r = requests.post('http://172.16.1.118:5000/receberDadosCliente', json = dados)
    print (r.json())

def main():

    dic = {}

    arquivo = open('/home/augusto/Documents/SD/ProjetoFinal/cliente/dadosTreinar.txt', 'r').read().split('\n')
    for i in range (0, len(arquivo)):
        arquivo[i] = arquivo[i].split(':')
        chave = (arquivo[i])[0]
        valor = (arquivo[i])[1]
        dic[chave] = str(valor)

    dic = json.dumps(dic)

    print (dic)

    enviarDadosMid(dic)



if __name__ == '__main__':
    main()