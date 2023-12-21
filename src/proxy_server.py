from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as xmlrpclib


class ProxyServer:
    def __init__(self, client_count):
        # 用户名和密码
        self.users = {
            '1': '1',
            '2': '2',
            '3': '3',
        }
        # 初始化代理服务器，设置客户端连接状态和服务器列表
        self.client_ids = [False] * client_count  # 用于标记客户端是否连接的列表
        # 连接到不同的服务器节点，服务器的基地址是20000
        self.servers = [xmlrpclib.ServerProxy(f'http://localhost:{20000 + i}') for i in range(client_count)]

    # 分配客户端ID
    def get_id(self):
        for i, connected in enumerate(self.client_ids):
            if not connected:
                self.client_ids[i] = True
                print(f'客户端 {i} 登录')
                return i
        print('没有可用的 ID')
        return None

    # 处理客户端发来的命令
    def function(self, client_id, clause):
        clause = clause.strip().split()  # 解析命令
        lens = len(clause)

        if lens < 1:
            return '错误的命令。输入 help 查看帮助信息。'

        command = clause[0]

        # 检查命令类型
        if command in ['PUT', 'GET', 'DELETE', 'LIST', 'LOG', 'EXIT']:
            # 获取对应的方法
            server_function = getattr(self, command.lower())
            return server_function(client_id, clause)
        else:
            return '错误的命令。输入 help 查看帮助信息。'

    # 处理客户端退出命令
    def exit(self, client_id, clause):
        self.client_ids[client_id] = False
        print(f'客户端 {client_id} 退出')
        return f'客户端 {client_id} 退出'

    # 实现PUT方法
    def put(self, client_id, clause):
        if len(clause) != 3:
            return '错误的命令格式。使用方法: PUT key value'

        key, value = clause[1], clause[2]
        if self.servers[client_id].put(key, value):
            return f"成功添加/更新key {key}，value {value}"
        return f"无法添加/更新key {key}，value {value}"

    # 实现GET方法
    def get(self, client_id, clause):
        if len(clause) != 2:
            return '错误的命令格式。使用方法: GET key'

        key = clause[1]
        value = self.servers[client_id].get(key)
        return f"key {key} 的value为：{value if value is not None else '[未找到value]'}"

    # 实现LIST方法
    def list(self, client_id, clause):
        if len(clause) != 1:
            return '错误的命令格式。使用方法: LIST'

        return self.servers[client_id].list()

    # 实现DELETE方法
    def delete(self, client_id, clause):
        if len(clause) != 2:
            return '错误的命令格式。使用方法: DELETE key'

        key = clause[1]
        if self.servers[client_id].delete(key):
            return f"删除key {key} 成功"
        return f"不存在，无法删除key {key}"

    # 实现LOG方法
    def log(self, client_id, clause):
        if len(clause) != 1:
            return '错误的命令格式。使用方法: LOG'

        return self.servers[client_id].get_log()

    # 登陆验证
    def authenticate(self, username, password):
        if username not in self.users:
            print('不存在该用户名，请重试！')
            return False
        elif self.users[username] != password:
            print('密码错误，请重试！')
            return False
        else:
            return True


if __name__ == '__main__':
    count = int(input('输入客户端数量: '))
    proxy = ProxyServer(client_count=count)
    server = SimpleXMLRPCServer(('localhost', 21000), allow_none=True)
    server.register_instance(proxy)

    print(f"代理服务器正在运行...")
    server.serve_forever()
