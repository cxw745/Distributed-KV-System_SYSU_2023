import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# 这里模拟数据库
log = []
database = {}
database_lock = threading.Lock()


class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.cache = {}  # 每个服务器实例的缓存字典

    def put(self, key, value):
        # 存储键值对到数据库并更新缓存
        with database_lock:
            database[key] = value
            self.cache[key] = value  # 添加/更新缓存
            msg = f"添加/更新key：{key}，value：{value}"
            self.write_log(msg)
            return True

    def get(self, key):
        # 先检查缓存，如果存在于缓存中则直接返回
        if key in self.cache:
            return self.cache[key]

        # 如果不在缓存中，则从数据库中获取，并更新缓存
        with database_lock:
            value = database.get(key)
            if value:
                self.cache[key] = value  # 如果在数据库中找到，则更新缓存
            return value

    def delete(self, key):
        # 从数据库中删除键值对，并从缓存中删除
        with database_lock:
            if key in database:
                del database[key]
                if key in self.cache:
                    del self.cache[key]  # 从缓存中删除
                msg = f"删除key：{key}"
                self.write_log(msg)
                return True
        return False

    def list(self):
        # 返回整个数据库
        with database_lock:
            return database

    def get_log(self):
        # 返回服务器日志
        with database_lock:
            return log

    def write_log(self, msg):
        # 记录服务器操作相关的日志
        log.append(f"服务器 {self.server_id}：{msg}")
        return True


def run_server(server_id):
    # 启动和运行 XML-RPC 服务器
    server = SimpleXMLRPCServer(("localhost", 20000 + server_id), requestHandler=SimpleXMLRPCRequestHandler)
    server.register_instance(Server(server_id))
    print(f"服务器 {server_id} 正在运行在端口 {20000 + server_id}\n")
    server.serve_forever()


if __name__ == "__main__":
    # 输入服务器数量并启动相应数量的线程
    count = int(input('输入服务器数量：'))
    threads = []

    for i in range(count):
        server_thread = threading.Thread(target=run_server, args=(i,))
        threads.append(server_thread)
        server_thread.start()
