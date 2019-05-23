import http.server, json
import sys
sys.path.append('/home/wmj/Projects/chengyudasai22/')
import content_type

score_names = ["第一轮", "第二轮", "特别环节", "第三轮", "第四轮"]
group_names = ["第一组", "第二组", "第三组", "第四组", "第五组", "第六组", 
               "第七组", "第八组", "第九组", "第十组", "第十一组", "第十二组", "第十三组", "第十四组"]


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
                with open(path) as f:
                    self.send_response(200)
                    self.send_header('Content-type', content_type.content_type.get(path.split('.')[-1], 'text/plain'))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f.read().encode())
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

    def do_OPTIONS(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Max-Age', 1000)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{}')


if __name__ == '__main__':
    server = http.server.HTTPServer(('127.0.0.1', 8000), Server)
    server.serve_forever()
