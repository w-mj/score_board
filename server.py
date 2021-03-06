import http.server, json
import sys
import threading
from simple_websocket_server import WebSocketServer, WebSocket
sys.path.append('.')
import content_type

responder_status = 2  # 2 未开始, 1 已开始， 0已抢答
mutex = threading.Lock()
ws_client = []
responder_client = []
class WsServer(WebSocket):
    def handle(self):
        # 收到数据，在self.data中
        global responder_status
        msg = json.loads(self.data)
        if msg['act'] != 'responder_state':
            print('receive: ' + self.data)
        if msg['act'] == 'race':
            mutex.acquire()
            if responder_status == 1:
                self.send_message('{"act": "success"}')
                responder_status -= 1
            mutex.release()
        elif msg['act'] == 'reset':
            mutex.acquire()
            responder_status = 2
            for c in ws_client:
                c.send_message('{"act": "reset"}')
            mutex.release()
        elif msg['act'] == 'start':
            mutex.acquire()
            if responder_status == 2:
                responder_status = 1
            mutex.release()
        elif msg['act'] == 'I AM RESPONDER!':
            if self not in responder_client:
                responder_client.append(self)
        elif msg['act'] == 'responder_state':
            self.send_message(json.dumps(
                {'act': 'responder_state',
                'state': [responder_status, len(responder_client)]}
                ))


    def connected(self):
        print(self.address, 'connected')
        ws_client.append(self)

    def handle_close(self):
        ws_client.remove(self)
        responder_client.remove(self)
        print(self.address, 'closed')


score_names = ["第一轮", "第二轮", "特别环节", "第三轮", "第四轮"]
group_names = ["第一组", "第二组", "第三组", "第四组", "第五组", "第六组", 
               "第七组", "第八组"]


try:
    with open('score.json') as f:
        score_dict = json.loads(f.read())
except:
    score_dict = [{"id": i, "name": x, "scores": [0 for _ in score_names], "out":False}
                for i, x in enumerate(group_names)]

def default_sort_func(a, b):
    return a["id"] - b["id"]

def sort_func(a, b):
    for i in range(len(score_names), -1, -1):
        if a['scores'][i] != b['scores'][i]:
            return a['scores'][i] - b['scores'][i]
    return a['id'] - b['id']

class Server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # url = self.path.split('/')
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps([score_names, score_dict]).encode())
        else:
            path = self.path[1:]
            try:
                with open(path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', content_type.content_type.get(path.split('.')[-1], 'text/plain'))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(('404 Not Found ' + self.path).encode())

            

    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('content-length')))
        data = json.loads(data.decode())
        if data['act'] == 'score':
            data = data['score']
            [x for x in score_dict if x['name'] == data[0]][0]['scores'][data[1]] += data[2]
        elif data['act'] == 'out':
            data = data['out']
            [x for x in score_dict if x['name'] == data[0]][0]['out'] = data[1]
        elif data['act'] == 'sort':
            if data['sort']:
                score_dict.sort(key=lambda x: list(reversed(x['scores'])), reverse=True)
            else:
                score_dict.sort(key=lambda x: x['id'])

        with open("score.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(score_dict, ensure_ascii=False))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write('{"result": "ok"}'.encode())

        to_send = json.dumps(
            {'act': 'score', 'score': [score_names, score_dict]})
        for client in ws_client:
            client.send_message(to_send)

    def do_OPTIONS(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Max-Age', 1000)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{}')

ip = '0.0.0.0'
def ws_server():
    print('Start Websocket server at ' + ip + ' 8001.')
    server = WebSocketServer(ip, 8001, WsServer)
    server.serve_forever()

if __name__ == '__main__':
    t = threading.Thread(target=ws_server)
    t.start()
    print('Start Http server at ' + ip + ' 8000.')
    server = http.server.HTTPServer((ip, 8000), Server)
    server.serve_forever()
    t.join()
