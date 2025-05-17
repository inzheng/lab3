
# US/app.py
from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

US_PORT = 8080

@app.route("/fibonacci", methods=["GET"])
def handle_fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Missing parameters", 400

    query_msg = f"TYPE=A\nNAME={hostname}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query_msg.encode(), (as_ip, int(as_port)))
    sock.settimeout(2)
    try:
        data, _ = sock.recvfrom(1024)
        response = data.decode()
        record = dict(line.split('=') for line in response.strip().split('\n'))
        fs_ip = record.get("VALUE")
        if not fs_ip or fs_ip == "0.0.0.0":
            return "Hostname not found", 404
    except socket.timeout:
        return "DNS query timed out", 504
    finally:
        sock.close()

    try:
        fib_response = requests.get(f"http://{fs_ip}:{fs_port}/fibonacci", params={"number": number})
        return (fib_response.text, fib_response.status_code)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=US_PORT)
