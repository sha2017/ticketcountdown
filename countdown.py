# pip3 install mysqlclient
import MySQLdb
import http.server

DATABASE_HOST = 'localhost'
DATABASE_USER = 'pretix'
DATABASE_PASS = ''
DATABASE_DB = 'pretix'

SERVER_IP = '0.0.0.0'
SERVER_PORT = 4242

MAX_TICKETS = 3650


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        return self.do_GET()

    def do_GET(self):

        if self.path != "/index.json":
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Ticket counter sponsored by E Corp. Try index.json.\n".encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.numbers().encode("utf-8"))

    def log_message(self, format, *args):
        return

    def numbers(self):
        db = MySQLdb.connect(host=DATABASE_HOST,
                             user=DATABASE_USER,
                             passwd=DATABASE_PASS,
                             db=DATABASE_DB)
        cur = db.cursor()
        cur.execute("""select 
                count(pretixbase_orderposition.item_id) as count,
                max(pretixbase_order.datetime) as latest
            FROM
                pretixbase_order
            INNER JOIN 
                pretixbase_orderposition on pretixbase_orderposition.order_id = pretixbase_order.id
            INNER JOIN
                pretixbase_item ON pretixbase_orderposition.item_id = pretixbase_item.id
            WHERE
                pretixbase_item.admission=1
            AND
                pretixbase_order.status IN ('p','n')""")

        answer = ""
        for row in cur.fetchall():
            number_sold = int(row[0])

            if number_sold >= MAX_TICKETS:
                answer = ("{\"ordered\":%d, \"last_order\":\"2017-08-04 13:37:23.424242\", \"tickets_left\":0}\n" %
                          MAX_TICKETS)
            else:
                answer = ("{\"ordered\":%d, \"last_order\":\"%s\", \"tickets_left\":%d}\n" %
                          (row[0], row[1], MAX_TICKETS - number_sold))

        db.close()

        return answer

server = http.server.HTTPServer((SERVER_IP, SERVER_PORT), MyHandler)
server.serve_forever()
