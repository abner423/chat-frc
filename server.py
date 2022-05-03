import socket
import threading
from collections import namedtuple

# Seta o host e a porta em que esse servidor vai ficar disponivel
host = '127.0.0.1'
port = 55555

# Sobe o servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lista de clientes e salas disponiveis
clients = []
rooms = []

# Lista os participantes da sala desejada
def listParticipants(room):
    participants = 0
    data = []
    for index, item in enumerate(clients):
        if item.room == room:
            data.append(item.nickname)
            participants += 1
    return 'participants: {}, total: {}'.format(data, participants)

# Lista todas as salas criadas
def listRooms():
    return 'rooms: {}'.format(rooms)

# Checka se uma sala já existe
def existsRoom(roomCheck):
    flag = False
    for room in rooms:
        if room == roomCheck:
            flag = True
    return flag

# Muda o usuario para a sala desejada
def changeRoom(actualRoom, newRoom ,nickname, indexUser):
    # Manda para os usuarios da sala que o usuario X estava que ele saiu dela
    message = {'value': '{} saiu!'.format(nickname).encode('ascii'), 'room': actualRoom}
    object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
    broadcast(object_message)

    # Manda para os usuarios da sala nova que o usuario X entrou nela
    message = {'value': "{} entrou!".format(nickname).encode('ascii'), 'room': newRoom}
    object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
    broadcast(object_message)

    # Altera a sala que o cliente
    clientToSet = clients.pop(indexUser)
    clientW = {'client': clientToSet.client, 'room':newRoom, 'nickname': nickname}
    object_w = namedtuple("ObjectName", clientW.keys())(*clientW.values())
    clients.append(object_w)

    
# Realiza o envio das mensagens para os usuarios da mesma sala que o emissor
def broadcast(message):
    for clientWithRoom in clients:
        if clientWithRoom.room == message.room:
            clientWithRoom.client.send(message.value)


# Função associada ao gerenciamento das mensagens
def handle(client):
    while True:
        try:
            # Pega o index do client que ta realizando o envio da mensagem
            for index, item in enumerate(clients):
                if item.client == client:
                    break
                else:
                    index = -1
            # Pega a sala do client que ta realizando o envio da mensagem
            roomToSend = clients[index].room
            # Pega o nickname do client que ta realizando o envio da mensagem
            nicknameUser = clients[index].nickname
            # Pega a mensagem do client que ta realizando o envio da mensagem
            message = {'value': client.recv(1024), 'room': roomToSend}
            object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
            valueToCompare = object_message.value.decode('ascii')
            # Verifica se a mensagem enviada é /lp, se for ele lista os participantes da sala do emissor
            if valueToCompare == '/lp':
                client.send(listParticipants(object_message.room).encode('ascii'))
            # Verifica se a mensagem enviada é /ls, se for ele lista as salas disponiveis da aplicacao
            elif valueToCompare == '/ls':
                client.send(listRooms().encode('ascii'))
            # Verifica se a mensagem enviada é /ts, se for ele troca o usuario para a sala desejada caso ela exista, se não avisa ao usuario que a sala nao existe
            elif '/ts' in valueToCompare:
                if existsRoom(str(valueToCompare).split(':')[1]):
                    changeRoom(roomToSend, str(valueToCompare).split(':')[1],nicknameUser, index)
                else:
                     client.send("Sala inexistente".encode('ascii'))
            # Verifica se a mensagem enviada é /cs, se for ele cria a sala troca o usuario para a sala desejada caso ela exista, se não avisa ao usuario que a sala ja existe
            elif '/cs' in valueToCompare:
                if not existsRoom(str(valueToCompare).split(':')[1]):
                    rooms.append(str(valueToCompare).split(':')[1])
                    changeRoom(roomToSend, str(valueToCompare).split(':')[1],nicknameUser, index)
                else:
                     client.send("Sala já existe".encode('ascii'))
            # Caso a mensagem não seja nenhum comando, ele so distribui ela aos usuarios da sala do emissor
            else:
                broadcast(object_message)
        except:
            # Caso seja encerrada a conexao ou ocorra uma excecao ele retira o client da sala e avisa aos usuarios que ele saiu daquela sala
            for index, item in enumerate(clients):
                if item.client == client:
                    break
                else:
                    index = -1
            
            removerCliente = clients[index]
            clients.remove(removerCliente)
            client.close()

            message = {'value': '{} saiu!'.format(removerCliente.nickname).encode('ascii'), 'room': removerCliente.room}
            object_message = namedtuple("ObjectMessage", message.keys())(*message.values())

            broadcast(object_message)
            break

# Função associada a conexao do client ao servidor
def receive():
    while True:
        # Aceita a conexão do client
        client, address = server.accept()
        print("Connectado com {}".format(str(address)))

        # Envia uma mensagem NICK para que o client mande o nickname e a sala desejada
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        # Verifica se essa sala já existe, se ja existe apenas coloca o usuario nela, se nao existir ele cria
        room = client.recv(1024).decode('ascii')
        if not existsRoom(room):
            rooms.append(room)

        # Associa o client a sala e ao nick dele
        clientWithRoom = {'client': client, 'room':room, 'nickname': nickname}
        object_name = namedtuple("ObjectName", clientWithRoom.keys())(*clientWithRoom.values())
        clients.append(object_name)
        print(object_name.nickname)

        print("Nome do usuário é {}".format(nickname))

        # Avisa aos usuarios da sala que o usuario X entrou, e inicia o handle de mensagens
        message = {'value': "{} entrou!".format(nickname).encode('ascii'), 'room': room}
        object_message = namedtuple("ObjectMessage", message.keys())(*message.values())

        broadcast(object_message)
        client.send('Connectado ao servidor!'.encode('ascii'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Servidor ligado")
receive()
