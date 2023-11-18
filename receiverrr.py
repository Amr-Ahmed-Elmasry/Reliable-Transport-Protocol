from socket import *
from binascii import hexlify, unhexlify
from Decapsulation import deSegment, readImg
import random
import time

raw_data_sm = readImg('SmallFile.png')
raw_data_md = readImg('MediumFile.jpg')
raw_data_lg = readImg('LargFile.jpg')

data_skt = socket(AF_INET, SOCK_DGRAM)
ack_skt = socket(AF_INET, SOCK_DGRAM)

#for sending
# server_IP = '172.20.10.4'
server_IP = 'localhost'
port_no = 1234 
ack_skt.bind((server_IP, port_no))

while True:
    data = bytes()
    message = input('input message: ')

    data_skt.sendto(message.encode(), (server_IP, 5555))

    confirmation, sender_address = data_skt.recvfrom(4096) #sender address da hb3at 3aleh acksss

    print(confirmation.decode())

    expected = 0
    last_correct = 0
    init_time = time.time()
    final_time = -1
    num_packets = 0
    while True:
        #time.sleep(0.0001)
        segment = data_skt.recv(4096) #input buffer size (powers of 2)

        ID_packet, ID_file, datum, trailer, length = deSegment(segment) #check trailer thing

        if ID_packet < expected: #lw ack l haga adema afkslha
            continue

        #some randomness to check out of order packets
        random.seed(time.time())
        rand = random.randint(0, 100)
        if rand <= 10 and ID_packet != 0:
            print(f'error at: {ID_packet}')
            ID_packet += 100


        if ID_packet != expected: #lw msh al expected ab3at al last correct ack
            ack = hexlify(last_correct.to_bytes(2,"little")) + hexlify(ID_file.to_bytes(2,"little"))
            print(f'recieved {ID_packet}, but not as expected {expected}')
            ack_skt.sendto(ack, sender_address)
            continue

        if ID_packet == 20000:
            time.sleep(1)

        #lw expected
        print(f'received ID: {ID_packet}')
        last_correct = ID_packet
        expected += int(length / 2)
        expected %= 2**16
        
        data += datum

        #send ack
        ack = hexlify(ID_packet.to_bytes(2,"little")) + hexlify(ID_file.to_bytes(2,"little"))
        ack_skt.sendto(ack, sender_address)
        num_packets += 1

        if trailer == b'f' * 8:
            print('=========Terminating...')
            final_time = time.time()
            break
    
    with open('receiver3.png', 'wb') as f:
        f.write(data)

    if (message == 'small'):
        print(raw_data_sm == data)
    if (message == 'medium'):
        print(raw_data_md == data)
    if (message == 'large'):
        print(raw_data_lg == data)
        
    # Stats
    elapsed_time = final_time -init_time
    print('==========Stats===========')
    print(f"start time: {init_time}")
    print(f"end time: {final_time}")
    print(f"elapsed time: {elapsed_time }")
    print(f"# of packets: {num_packets}")
    print(f"# of bytes: {len(data)}")
    print(f"average transfer rate (byte/s): {len(data)/elapsed_time}")
    print(f"average transfer rate (packet/s): {num_packets/elapsed_time}")
    print('==========================')


#recv_skt.close()