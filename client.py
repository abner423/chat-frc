from operator import contains
import socket
import threading


# Coleta os primeiros dados de nickname desejado e a sala que deseja entrar ou criar para mandar para o servidor
nickname = input("Escolha seu nome de usuário: ")
sala = input("Digite a sala que deseja entrar ou criar: ")
trocaSala = False

# Conecta ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Funcao associada a thread de recebimento de mensagens
def receive():
    global trocaSala
    # Roda o loop enquanto o usuario nao digita o comando /sair
    while not trocaSala:
        try:
            # Recebe uma mensagem do servidor
            message = client.recv(1024).decode('ascii')
            # Verifica se essa mensagem é 'NICK' (mensagem especificada para envio de nickname e a sala para o servidor)
            if message == 'NICK':
                # Envia o nickname e a sala para o servidor
                client.send(nickname.encode('ascii'))
                client.send(sala.encode('ascii'))
            else:
                # Caso não seja NICK, ele printa a mensagem enviada por outros usuarios na tela
                print(message)
        except:
            # Caso ocorra uma exceção, encerra conexão com o servidor e para a execucao do codigo
            client.close()
            break

# Funcao associada a thread de escrita de mensagens
def write():
    global trocaSala
    # Roda o loop enquanto o usuario nao digita o comando /sair
    while not trocaSala:
        # Digita a mensagem que vai ser enviada aos participantes da sala
        dadoDigitado = input('')
        # Caso essa mensagem seja /menu ele não envia a mensagem ao servidor e lista os comandos disponiveis para o usuario
        if dadoDigitado == '/menu':
            print('Lista de comandos disponíveis:')
            print('Listar participantes da sala atual: /lp')
            print('Listar salas disponíveis: /ls')
            print('Trocar de sala: /ts:nome_da_sala')
            print('Criar nova sala: /cs:nome_da_sala')
        # Caso essa mensagem seja /lp ele envia a mensagem ao servidor para que o servidor mande de volta os participantes dessa sala
        elif dadoDigitado == '/lp':
            client.send(dadoDigitado.encode('ascii'))
        # Caso essa mensagem seja /ls ele envia a mensagem ao servidor para que o servidor mande de volta as salas disponíveis no momento
        elif dadoDigitado == '/ls':
            client.send(dadoDigitado.encode('ascii'))
        # Caso essa mensagem seja /ts ele envia a mensagem ao servidor para que o servidor troque esse usuario de sala
        elif '/ts' in dadoDigitado:
            if ':' not in dadoDigitado or dadoDigitado.split(':')[1].strip() == '':
                print("Dado inválido para troca de sala")
            else:
                client.send(dadoDigitado.encode('ascii'))
        # Caso essa mensagem seja /cs ele envia a mensagem ao servidor para que o servidor crie uma sala e troque esse usuario de sala
        elif '/cs' in dadoDigitado:
            if ':' not in dadoDigitado:
                print("Dado inválido para criação de sala")
            else:
                client.send(dadoDigitado.encode('ascii'))
        # Caso essa mensagem seja /sair o client encerra conexao com o servidor e para a execucao do codigo
        elif dadoDigitado == '/sair':
            trocaSala = False
            client.close()
            break
        # Caso não seja nenhum dos comandos disponíveis ele apenas formata a mensagem e envia para que o servidor distribua a todos os usuarios dessa sala
        else:
            message = '{}: {}'.format(nickname, dadoDigitado)
            client.send(message.encode('ascii'))


# Abre uma thread para receber mensagens
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Abre uma thread para escrever as mensagens
write_thread = threading.Thread(target=write)
write_thread.start()
