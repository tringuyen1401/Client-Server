import socket,sys,json,argparse   #for sockets,system,json, arg parsing
import traceback #for Exception handling
from thread import * #for heartbeat thread

#initialized the host,port and my name
host = 'localhost';
port = 8888; 
#save the message to send to other users while waiting for reply from server
sending_msg =  ''
#my name
name = ''

#parsing the args
def main():
    global name,host,port

    p = argparse.ArgumentParser()
    #server ip, set default to be localhost
    p.add_argument('-sip','--server',default='localhost')
    #server port, set default to 8888
    p.add_argument('-sp','--port', type=int, default =8888)
    #user name, compulsory
    p.add_argument('-u','--user', required=True)

    args = p.parse_args()
    #modify the host,port and user name
    port = args.port
    host = args.server
    name = args.user

main()

#create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sending sign-in message to the server once socket is established
    msg = {}
    msg['type'] = 'signin'
    msg['user'] = name 
    s.sendto(json.dumps(msg), (host,port))
except socket.error:
    print 'Failed to create socket'
    sys.exit()
 
#recving thread, so the user's input won't block us from listening and displaying 
#message from server
def recvthread():
    global sending_msg
    while 1:
        d = s.recvfrom(1024)
        reply = json.loads(d[0])
        addr = d[1]
        sen = {}
        try:
            #print/reply to server accordingly based on the msg's type
            if reply['type'] == 'list':                
                sys.stdout.write('<- Signed In Users: ' + str(reply['list'])+'\n+> ')
                sys.stdout.flush()
            elif reply['type'] == 'send':                    
                #for send, we retrieve the ip,port and then
                #send the message to be sent from sending_msg
                sen['type'] = 'message'
                sen['message'] = sending_msg
                sen['src'] = name
                s.sendto(json.dumps(sen),  (reply['addr'][0], reply['addr'][1]))
                sending_msg = ''
            elif reply['type'] == 'message':
                #if we receive some message from other people,display it
                sys.stdout.write('\r<- <From '+str(addr[0])+':'+str(addr[1])+':'+reply['src']+'>:'+reply['message']+'\n+> ')
                sys.stdout.flush()
            #reply to the server that we are alive
            elif reply['type'] == 'hb':
                sen['type'] = 'hb'                
                sen['name'] = name
                s.sendto(json.dumps(sen), addr)
        except Exception:
            print traceback.format_exc()
 
start_new_thread(recvthread, ())
#promt for user input
sys.stdout.write('+> ')
sys.stdout.flush()
while(1) :
    msg = raw_input('')
     
    try :
        sen = {}
        #check for the command
        if msg.split()[0] == 'list':
            sen['type'] = 'list'
            s.sendto(json.dumps(sen), (host, port))
        elif msg.split()[0] == 'send':
            
            sen['type'] = 'send'
            sen['user'] = msg.split()[1]
            #i choose this way to get the message
            #assuming the users follow the rules
            #inputing the send command
            slen = 6 + len(msg.split()[1])
            #save the message to be sent and wait for
            #reply from the server
            sending_msg = msg[slen:]
            s.sendto(json.dumps(sen), (host, port))            
            sys.stdout.write('+> ')
            sys.stdout.flush()
      #if the command not list or send,ignore
        else:
            sys.stdout.write('+> ')
            sys.stdout.flush()
 
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
