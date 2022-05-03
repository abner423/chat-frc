from operator import contains
import socket
import threading


nickname = input("Escolha seu nome de usuário: ")
sala = input("Digite a sala que deseja entrar ou criar: ")
trocaSala = False


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    global trocaSala
    while not trocaSala:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                client.send(sala.encode('ascii'))
            else:
                print(message)
        except:
            client.close()
            break


def write():
    global trocaSala
    while not trocaSala:
        dadoDigitado = input('')
        if dadoDigitado == '/menu':
            print('Lista de comandos disponíveis:')
            print('Listar participantes da sala atual: /lp')
            print('Listar salas disponíveis: /ls')
            print('Trocar de sala: /ts:nome_da_sala')
            print('Criar nova sala: /cs:nome_da_sala')
        elif dadoDigitado == '/lp':
            client.send(dadoDigitado.encode('ascii'))
        elif dadoDigitado == '/ls':
            client.send(dadoDigitado.encode('ascii'))
        elif '/ts' in dadoDigitado:
            if ':' not in dadoDigitado or dadoDigitado.split(':')[1].strip() == '':
                print("Dado inválido para troca de sala")
            else:
                client.send(dadoDigitado.encode('ascii'))
        elif '/cs' in dadoDigitado:
            if ':' not in dadoDigitado:
                print("Dado inválido para criação de sala")
            else:
                client.send(dadoDigitado.encode('ascii'))
        elif dadoDigitado == '/sair':
            trocaSala = False
            client.close()
            break
        else:
            message = '{}: {}'.format(nickname, dadoDigitado)
            client.send(message.encode('ascii'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
