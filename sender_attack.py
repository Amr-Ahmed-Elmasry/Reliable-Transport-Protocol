from binascii import hexlify, unhexlify
import time
from Decapsulation import deSegment_ack, deSegment,calculate_timeout_rtt,fixN
import matplotlib.pyplot as plt
import math


#initializations
file_name = ''
Ip_address = ''
port_no = 5555
MSS = 1008 #maximum segment size
time_out = 0.2 #min time out value in seconds
ID_packet = 0
ID_file = 0
data_size = MSS - 8 #size of the payload in bytes
#byte ya3ny rkamen hexa
no_of_hexa = data_size * 2 #length of the payload in hexa
trailer = b'0' * 8

#From here the server part
from socket import *

#socket initialization
data_skt = socket(AF_INET, SOCK_DGRAM)
ack_skt = socket(AF_INET, SOCK_DGRAM)

server_IP = 'localhost' #directly hyakhod IP al machine
port_no = 5555

data_skt.bind((server_IP, port_no)) #declare port ll server 3shan ba2y al clients tb3at 3aleh

# N = N * no_of_hexa #window size in hexa

while(True):

    print('Here we go')
    message, sender_address = data_skt.recvfrom(4096) #unknown recv_socket (2ly hb3at 3aleh dataaa)

    confirmation = 'Here you go!'
    ack_skt.sendto(confirmation.encode(), sender_address)

    message = message.decode()

    #reading the image in bytes and turning it into hexa digits
    if message == 'small':
        file_name = 'SmallFile.png'
    elif message == 'medium':
        file_name = 'MediumFile.jpg'
    elif message == 'large':
        file_name = 'LargFile.jpg'
    else:
        message = 'Invalid'
        message = message.encode()
        data_skt.sendto(message, sender_address)
        continue
    
    data = ''
    raw_data = ''
    with open(file=file_name, mode='rb') as image:
        raw_data = image.read()
        data = hexlify(raw_data)

    base = 0 #base of the window
    thres = 0 #first unsent packet
    iterations = 0 #number of iterations (one iteration means finishing the packet ID space)
    last_ack = -1 #last acknowledged packet
    j = 0
    ID_packet = 0
    trailer = b'0' * 8
    start = time.time()
    rtt_list = []
    rtt_dev_list = []
    n_list = []
    to_list = []
    last_packet_acked = False
    
    N = 1 * no_of_hexa # initial window size of Go-Back-N
    maxN = 20 * no_of_hexa # Max window size
    minN = 1 * no_of_hexa # Min window size
    
    # for plotting
    packet_ids = []
    times = []
    
    # Stats
    init_time = time.time()
    final_time = -1
    
    while True:
        pass
    
    ID_file += 1