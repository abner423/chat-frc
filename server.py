import socket
import threading
from collections import namedtuple


host = '127.0.0.1'
port = 55555


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
rooms = []

def listParticipants(room):
    participants = 0
    data = []
    for index, item in enumerate(clients):
        if item.room == room:
            nickname = nicknames[index]
            data.append(nickname)
            participants += 1
    return 'participants: {}, total: {}'.format(data, participants)

def listRooms():
    return 'rooms: {}'.format(rooms)

def existsRoom(roomCheck):
    flag = False
    for room in rooms:
        if room == roomCheck:
            flag = True
    return flag

def changeRoom(actualRoom, newRoom ,nickname, indexUser):
    message = {'value': '{} saiu!'.format(nickname).encode('ascii'), 'room': actualRoom}
    object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
    broadcast(object_message)

    message = {'value': "{} entrou!".format(nickname).encode('ascii'), 'room': newRoom}
    object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
    broadcast(object_message)

    clientToSet = clients.pop(indexUser)
    
    # clientToSet.room = newRoom
    clientW = {'client': clientToSet.client, 'room':newRoom}
    object_w = namedtuple("ObjectName", clientW.keys())(*clientW.values())
    clients.append(object_w)

    

def broadcast(message):
    for clientWithRoom in clients:
        if clientWithRoom.room == message.room:
            clientWithRoom.client.send(message.value)


def handle(client):
    while True:
        try:
            for index, item in enumerate(clients):
                if item.client == client:
                    break
                else:
                    index = -1

            roomToSend = clients[index].room
            nicknameUser = nicknames[index]
            message = {'value': client.recv(1024), 'room': roomToSend}
            object_message = namedtuple("ObjectMessage", message.keys())(*message.values())
            valueToCompare = object_message.value.decode('ascii')
            if valueToCompare == '/lp':
                client.send(listParticipants(object_message.room).encode('ascii'))
            elif valueToCompare == '/ls':
                client.send(listRooms().encode('ascii'))
            elif '/ts' in valueToCompare:
                print("aqui")
                if existsRoom(str(valueToCompare).split(':')[1]):
                    changeRoom(roomToSend, str(valueToCompare).split(':')[1],nicknameUser, index)
                else:
                     client.send("Sala inexistente".encode('ascii'))
            else:
                broadcast(object_message)
        except:
            for index, item in enumerate(clients):
                if item.client == client:
                    break
                else:
                    index = -1
                    
            removerCliente = clients[index]
            clients.remove(removerCliente)
            client.close()
            nickname = nicknames[index]

            message = {'value': '{} saiu!'.format(nickname).encode('ascii'), 'room': removerCliente.room}
            object_message = namedtuple("ObjectMessage", message.keys())(*message.values())

            broadcast(object_message)
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print("Connectado com {}".format(str(address)))

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        room = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        if not existsRoom(room):
            rooms.append(room)

        clientWithRoom = {'client': client, 'room':room}
        object_name = namedtuple("ObjectName", clientWithRoom.keys())(*clientWithRoom.values())
        clients.append(object_name)

        print("Nome do usuário é {}".format(nickname))

        message = {'value': "{} entrou!".format(nickname).encode('ascii'), 'room': room}
        object_message = namedtuple("ObjectMessage", message.keys())(*message.values())

        broadcast(object_message)
        client.send('Connectado ao servidor!'.encode('ascii'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Servidor ligado")
receive()
