import struct
import json

# Acest fisier asigura ca mesajele transmise prin TCP sunt delimitate corect.
# Prefixam fiecare mesaj cu lungimea sa pentru a sti unde se termina.

# Structura: [4 Bytes Lungime JSON] + [Date JSON] + [4 Bytes Lungime Binar] + [Date Binare]

def send_msg(sock, metadata, binary_data=b""):
    """Trimite metadata (JSON) si datele binare optionale."""
    json_bytes = json.dumps(metadata).encode('utf-8')
    
    # 'I' = unsigned int, '>' = Big Endian
    header_json = struct.pack('>I', len(json_bytes))
    header_bin = struct.pack('>I', len(binary_data))
    
    sock.sendall(header_json + json_bytes + header_bin + binary_data)

def recv_exact(sock, num_bytes):
    """Citeste exact numarul de bytes specificat din fluxul TCP."""
    data = bytearray()
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None 
        data.extend(packet)
    return bytes(data)

def recv_msg(sock):
    """Decodifica un pachet complet conform protocolului stabilit."""
    # 1. Citim lungimea JSON-ului
    raw_json_len = recv_exact(sock, 4)
    if not raw_json_len:
        return None, None 
    
    json_len = struct.unpack('>I', raw_json_len)[0]
    
    # 2. Citim continutul JSON
    json_bytes = recv_exact(sock, json_len)
    metadata = json.loads(json_bytes.decode('utf-8'))
    
    # 3. Citim lungimea datelor binare
    raw_bin_len = recv_exact(sock, 4)
    bin_len = struct.unpack('>I', raw_bin_len)[0]
    
    # 4. Citim datele binare
    binary_data = b""
    if bin_len > 0:
        binary_data = recv_exact(sock, bin_len)
        
    return metadata, binary_data