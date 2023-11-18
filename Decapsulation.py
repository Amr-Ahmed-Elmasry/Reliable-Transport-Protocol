from binascii import hexlify, unhexlify

def deSegment(segment):
    length = len(segment[8 : len(segment) - 8])
    ID_packet = unhexlify(segment[0 : 4])
    ID_file = unhexlify(segment[4 : 8])
    data = unhexlify(segment[8 : len(segment) - 8])
    trailer = segment[-8:]

    return (int.from_bytes(ID_packet,"little"), int.from_bytes(ID_file,"little"), data, trailer, length)

def deSegment_ack(ack):
    ID_packet = unhexlify(ack[0 : 4])
    ID_file = unhexlify(ack[4 : 8])

    return (int.from_bytes(ID_packet,"little"), int.from_bytes(ID_file,"little"))

def readImg(fileName):
    raw_data = b''
    with open(file=fileName, mode='rb') as image:
        raw_data = image.read()
        
    return raw_data

def calculate_timeout_rtt(rtt, dev_rtt):
    timeout = rtt + 4 * dev_rtt
    return timeout

def calculate_window_size(rtt, packet_loss_rate):
    window_size = int((rtt * 1.2) / packet_loss_rate)
    return window_size

def fixN(N,minN,maxN, no_of_hexa):
    N = N // no_of_hexa
    N = N * no_of_hexa
    if (N >= maxN):
        return maxN
    if(N <= minN):
        return minN
    
    return N