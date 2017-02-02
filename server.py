import socket,sys,json,time,argparse #for sockets,system,json,time checking and arg parsing
import traceback #for exception handling
from thread import * #for threading of the heartbeat
 
#initialized host,port and user list(dictionary)
host = ''   
port = 8888 
users = {}

def main():
    global port

    p = argparse.ArgumentParser()
    #parse the port 
    p.add_argument('-sp','--port', type=int, default =8888)

    args = p.parse_args()

    port = args.port

main()


#heart beat to check if the users are still connected, check every 1 second
def hbthread():
    try:
        while 1:
            clock = time.time()
            to_send = {}
            to_send['type'] = 'hb'
            #check each users,if there's no response after 1.6 seconds, delete
            for u in users.keys():
                if clock - users[u]['time'] > 1.6:
                    del users[u]
                #else, send the heartbeat every 0.5s
                elif clock - users[u]['time'] > 0.5 :
                    s.sendto(json.dumps(to_send), users[u]['addr'])
    except Exception:
        print traceback.format_exc()

# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((host, port))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Server Initialized...'

start_new_thread(hbthread, ())

#listen and reply to the clients
while 1:
    #listen from client
    d = s.recvfrom(1024)
    data = d[0]
    addr = d[1]
    reply = '' 
        
    try:
        #check check the msg's type and respond
        msg = json.loads(data)
        if msg['type'] == 'signin':
            name = msg['user']
            users[name] = {}
            #save address and log-in time, this means
            #the later log in will override the former
            users[name]['addr'] = addr
            users[name]['time'] = time.time()
        #if list, then return the list of users.keys()                
        elif msg['type'] == 'list':
            reply = {}
            reply['list'] = ''
            for u in users.keys():                
                if len(reply['list']) != 0: 
                    reply['list'] = reply['list'] + ', '+ u
                else:
                    reply['list'] = u
            reply['type'] = 'list'
        #if send, find the user's address and reply
        elif msg['type'] == 'send':
            #check if user is online,else ignore
            if msg['user'] in users.keys():
                try:
                    reply = {}
                    reply['type'] = 'send'
                    reply['addr'] = users[msg['user']]['addr']
                    
                except KeyError, e:
                    #if the user's name is not in the list,ignore
                    msg['type'] = 'hb'
                    continue
            else:
                #change the type of msg so it will be ignored
                msg['type'] = 'hb'
        #if heartbeat, just update the time
        elif msg['type'] == 'hb':
            users[msg['name']]['time'] = time.time()
        else:
            continue
    except ValueError, e:
        print e
    #if msg's type is not heart beat or signin, send the reply
    if msg['type'] not in  ('hb','signin'):
        s.sendto(json.dumps(reply) , addr)
        print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
       

s.close()
