
# AS/server.py
import socket

DNS_PORT = 53533
RECORD_FILE = "dns_records.txt"

# Helper: Parse DNS messages to dict
def parse_dns_message(message):
    lines = message.strip().split('\n')
    record = {}
    for line in lines:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            record[key.strip()] = value.strip()
    return record

# Helper: Save DNS record to file
def save_record(record):
    with open(RECORD_FILE, 'a') as f:
        line = f"{record['NAME']} {record['VALUE']} {record['TYPE']} {record['TTL']}\n"
        f.write(line)

# Helper: Search for DNS record
def search_record(name, rtype):
    try:
        with open(RECORD_FILE, 'r') as f:
            for line in f:
                n, val, t, ttl = line.strip().split()
                if n == name and t == rtype:
                    return {"NAME": n, "VALUE": val, "TYPE": t, "TTL": ttl}
    except FileNotFoundError:
        return None
    return None

# Main UDP server loop
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", DNS_PORT))
print(f"[AS] Authoritative Server running on UDP port {DNS_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()
    record = parse_dns_message(message)

    if 'VALUE' in record and 'TTL' in record:
        # This is a registration message
        save_record(record)
        print(f"[REGISTERED] {record}")
    else:
        # This is a query
        result = search_record(record['NAME'], record['TYPE'])
        if result:
            response = f"TYPE={result['TYPE']}\nNAME={result['NAME']}\nVALUE={result['VALUE']}\nTTL={result['TTL']}"
        else:
            response = "TYPE=A\nNAME=NOT_FOUND\nVALUE=0.0.0.0\nTTL=0"
        sock.sendto(response.encode(), addr)
        print(f"[RESPONSE] {response.replace(chr(10), ' | ')}")
