
# FS/app.py
from flask import Flask, request, jsonify
import socket
import json

app = Flask(__name__)

FS_HOSTNAME = "fibonacci.com"
FS_IP = "172.18.0.2"
FS_PORT = 9090

@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json()
    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = int(data.get("as_port"))

    if not all([hostname, ip, as_ip, as_port]):
        return "Missing parameters", 400

    message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (as_ip, as_port))
        sock.close()
        return "Registered", 201
    except Exception as e:
        return str(e), 500

@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    num = request.args.get("number")
    try:
        n = int(num)
        if n < 0:
            return "Negative number not allowed", 400
        fib = [0, 1]
        for i in range(2, n + 1):
            fib.append(fib[i - 1] + fib[i - 2])
        return jsonify({"fibonacci": fib[n]}), 200
    except (ValueError, TypeError):
        return "Invalid number", 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=FS_PORT)
