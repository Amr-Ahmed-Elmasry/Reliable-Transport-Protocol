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
    maxN = 1 * no_of_hexa # Max window size
    minN = 1 * no_of_hexa # Min window size
    
    # for plotting
    packet_ids = []
    times = []
    
    # Stats
    init_time = time.time()
    final_time = -1
    
    while True:
        N = fixN(N,minN,maxN, no_of_hexa)
        for j in range(thres, base + N, no_of_hexa): #sending the rest of the window
            if j + no_of_hexa >= len(data):
                print('last')
                trailer = b'f' * 8
            print(f'segment no. {ID_packet}')
            segment_data = data[j : j + no_of_hexa]
            ID_packet = int(ID_packet)
            segment = hexlify((ID_packet % 2**16).to_bytes(2,"little")) + hexlify(ID_file.to_bytes(2,"little")) + segment_data + trailer
            #time.sleep(0.0001)
            data_skt.sendto(segment, sender_address)
            rtt_start = time.time()
            packet_ids.append(ID_packet % 2**16)
            times.append(rtt_start)

            ID_packet += int(len(segment_data) / 2)
            iterations = ID_packet // 2**16 #the iteration number of the last sent packet
        
        thres = base + N
        
        t = time.time() - start
        if (time_out - t) <= 0: #timeouttt (readjust the base and set new timer)
            #tb w al ID packet!!
            steps = (thres - base) / no_of_hexa
            if ID_packet - steps <= 0:
                ID_packet += 2**16
            ID_packet -= steps

            thres = base #3shan ab3at akher window tani
            start = time.time()
            continue

        ack_skt.settimeout(time_out - t)
        
        try:
            ack = ack_skt.recv(4096) #receive acknowledgement
            ##############################
            rtt = time.time() - rtt_start
            rtt_list.append(rtt)
            
            # Calculate average RTT
            average_rtt = sum(rtt_list) / len(rtt_list)

            # Calculate deviation of RTT
            dev_rtt = (sum((rtt - average_rtt) ** 2 for rtt in rtt_list) / len(rtt_list)) ** 0.5
            rtt_dev_list.append(dev_rtt)
            
            # new timeout
            time_out = max(calculate_timeout_rtt(rtt,dev_rtt),0.2)
            n_list.append(N / no_of_hexa)
            to_list.append(time_out)
            
            N += 1 * no_of_hexa  # Increase the congestion window size additively
            ##############################
            ID_ack , _ID_file = deSegment_ack(ack) #decapsulation of the acknowledgment

            print(f'last ack {last_ack}, ack no. {ID_ack}')

            #update the base based on the acks, if base becomes outside the len(data) --> break as file is sent
            #two approaches: 1) 7awl ack id l equivalent byte address using no. of iterations 2)7awl base w base+N l equivalent ack id

            #trying second approach
            lower = (base // 2)  % 2**16 #lower base of the window
            upper = ((base + N) // 2) % 2**16 #upper base of the window

            #lw upper akbar mn lower fa enta tmam w lazem ack id mabenhom
            #lw lower akbar mn upper fa keda upper sabe2 b iteration w al ack id still akbar aw ad lower bs bardo akbar mn al upper

            #lw ack abl al window afkslha, lw ack ba3d al window afkslha
            #lw for packet alreaded acked then resend the window (2ly heya al packet 2ly ableya belzbt)
            #lw ack fel window, then update last acked, w update al base to last acked + 1
            
            print(f'lower is {lower}, upper is {upper}')
            if lower < upper:
                if ID_ack >= lower and ID_ack < upper: #keda al ack mazbota
                    last_ack = ID_ack
                    #update al base 3shan yb2a 2odam al last ack
                    diff = ID_ack - lower #difference ya3ny mabenhom kam byte
                    diff *= 2 #diff mabenhom kam hexa
                    base += diff * no_of_hexa
                    base += no_of_hexa

                    start = time.time() #restart the timer
                elif ID_ack == last_ack:
                    thres = base #3shan ab3at akher window tani
                    ID_packet = ID_ack + int(len(segment_data) / 2) #synchronize the packet id m3 al window

                    start = time.time() #restart the timer
                else:
                    pass #discard the ack lw heya akbar mn al window aw as8ar mnha except lw heya akher ack
            else:
                if ID_ack >= lower and ID_ack > upper or ID_ack < lower and ID_ack < upper: #lw al upper sabe2 al lower, ack gat 3and lower or gat 3and upper
                    last_ack = ID_ack
                    #update al base 3shan yb2a 2odam al last ack
                    if ID_ack < lower:
                        ID_ack += 2**16 #3shan akhleha fe mkanha akbar mnha 3shab a7seb al difference

                    diff = ID_ack - lower #difference ya3ny mabenhom kam byte
                    diff *= 2 #diff mabenhom kam hexa
                    base += diff * no_of_hexa
                    base += no_of_hexa

                    start = time.time() #restart the timer
                elif ID_ack == last_ack:
                    thres = base #3shan ab3at akher window tani
                    ID_packet = ID_ack + int(len(segment_data) / 2) #synchronize the packet id m3 al window

                    start = time.time() #restart the timer
                else:
                    pass #discard the ack lw heya akbar mn al window aw as8ar mnha except lw heya akher ack
        except:
            #tb w al ID packet!!
            N = N // 2
            print('[shit]', N)
            steps = (thres - base) / no_of_hexa
            if ID_packet - steps <= 0:
                ID_packet += 2**16
            ID_packet -= int(steps)
            thres = base #3shan ab3at akher window tani
            start = time.time()
            #print('inside timeout')
        
        if thres >= len(data):
            # Check if the last packet is acknowledged successfully
            if ID_packet >= len(data) / no_of_hexa:
                print('=========Terminating...')
                final_time = time.time()
                break
            else:
                thresh = base
    
    # Plotting
    times = [(x - times[0])*1000 for x in times]
    plt.scatter(times, packet_ids, marker='o',color='blue', label='Sent Packets')

    # Check for unique retransmissions
    retransmitted_packets = set()
    for i in range(1, len(packet_ids)):
        if packet_ids[i] in packet_ids[:i]:
            retransmitted_packets.add(packet_ids[i])
    
    # Check for all retransmissions
    retransmissions = {}
    for i in range(1, len(packet_ids)):
        packet_id = packet_ids[i]
        if packet_id in packet_ids[:i]:
            if packet_id not in retransmissions:
                retransmissions[packet_id] = 1
            else:
                retransmissions[packet_id] += 1

    if retransmitted_packets:
        # Mark retransmitted packets with a different color
        retransmitted_times = [times[i] for i in range(len(packet_ids)) if packet_ids[i] in retransmitted_packets]
        retransmitted_ids = [packet_ids[i] for i in range(len(packet_ids)) if packet_ids[i] in retransmitted_packets]
        plt.scatter(retransmitted_times, retransmitted_ids, marker='.',color='red', label='Retransmitted Packets')

    # Set plot labels and title
    plt.xlabel('Time (ms)')
    plt.ylabel('Packet ID')
    plt.title(f'Packet ID vs. Time - {file_name}')

    # Display the number of retransmissions and test parameters
    num_retransmissions = sum(value for value in retransmissions.values())
    num_bytes = len(raw_data)
    num_packets = math.ceil(num_bytes / data_size)
    elapsed_time = final_time - init_time
    average_transfer_rate_byte = num_bytes / elapsed_time
    average_transfer_rate_pack = num_packets / elapsed_time
    print('==========Stats===========')
    print(f"start time: {init_time}")
    print(f"end time: {final_time}")
    print(f"elapsed time: {elapsed_time}")
    print(f"# of packets: {num_packets}")
    print(f"# of bytes: {num_bytes}")
    print(f"# of retransmissions: {num_retransmissions}")
    print(f"average transfer rate (byte/s): {average_transfer_rate_byte}")
    print(f"average transfer rate (packet/s): {average_transfer_rate_pack}")
    print('==========================')
    
    
    parameters = f'Avg Window Size: {round(sum(n_list) / len(n_list),2)}\nAvg Timeout Interval: {round(sum(to_list) / len(to_list),2)}'  # Add the actual parameters
    plt.text(.08, .85, f'Retransmissions: {num_retransmissions}\n{parameters}', transform=plt.gca().transAxes,
            verticalalignment='center', horizontalalignment='center', bbox=dict(boxstyle="round",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))

    # Show the legend and plot
    plt.legend(loc='upper left')
    plt.show()
    

    ID_file += 1