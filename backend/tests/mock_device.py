import socket
import threading
import time
import paramiko
import re

HOST_KEY = paramiko.RSAKey.generate(2048)

class MockServerInterface(paramiko.ServerInterface):
    def __init__(self): self.event = threading.Event()
    def check_channel_request(self, kind, chanid): return paramiko.OPEN_SUCCEEDED
    def check_auth_password(self, username, password): return paramiko.AUTH_SUCCESSFUL
    def get_allowed_auths(self, username): return 'password'
    def check_channel_shell_request(self, channel): self.event.set(); return True
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes): return True

def handle_client(client_sock, addr):
    print(f"🔌 [MockDevice] 收到连接: {addr}")
    transport = None
    try:
        transport = paramiko.Transport(client_sock)
        transport.add_server_key(HOST_KEY)
        server = MockServerInterface()
        try:
            transport.start_server(server=server)
        except: return

        chan = transport.accept(20)
        if not chan: return
        server.event.wait(10)
        if not server.event.is_set(): return

        # 初始提示符
        chan.send("\r\nMockSwitch#")
        
        buffer = ""
        while True:
            try:
                data = chan.recv(1024).decode('utf-8', errors='ignore')
            except: break
            if not data: break
            
            buffer += data
            # ... (前面是 buffer += data)
            
            # 检测回车符 (命令结束)
            if '\n' in buffer or '\r' in buffer:
                cmd_line = buffer.strip()
                buffer = "" 
                
                if not cmd_line:
                    chan.send("\r\nMockSwitch#")
                    continue

                print(f"📩 [收到命令] {cmd_line}")

                # ★★★ 新增：优雅处理退出 ★★★
                if cmd_line == "exit":
                    print("👋 客户端请求断开连接")
                    break  # 直接跳出循环，不再尝试发送数据，自然断开

                response = "" # 默认无结果
                
                # ... (后面是正则匹配逻辑)
                
                # === 匹配逻辑 ===
                if re.match(r"^term(inal)?\s+(width|length).*", cmd_line, re.I):
                    response = "" # 初始化命令，静默成功
                elif re.match(r"^no\s+logging\s+console", cmd_line, re.I):
                    response = ""
                elif re.match(r"^sh(ow)?\s+ip\s+int.*", cmd_line, re.I):
                    response = (
                        "Interface              IP-Address      OK? Method Status                Protocol\r\n"
                        "GigabitEthernet0/1     192.168.1.1     YES manual up                    up\r\n"
                        "GigabitEthernet0/2     unassigned      YES unset  down                  down"
                    )
                elif re.match(r"^sh(ow)?\s+ver.*", cmd_line, re.I):
                    response = "Cisco IOS Software, Version 15.0(2)SE4\r\nSerial: FOC12345678"
                else:
                    response = "% Unknown command."

                # ★★★ 关键修复：命令回显 (Echo) ★★★
                # 真实逻辑：回车换行 -> 重复命令 -> 回车换行 -> 结果 -> 回车换行 -> 提示符
                
                output = f"\r\n{cmd_line}\r\n" # 1. 先把命令复读一遍给 Netmiko 看
                
                if response:
                    output += f"{response}\r\n" # 2. 如果有结果，加上结果
                
                output += "MockSwitch#" # 3. 最后加提示符
                
                chan.send(output)

    except Exception as e:
        print(f"⚠️ 异常: {e}")
    finally:
        if transport: transport.close()
        client_sock.close()
        print(f"👋 关闭: {addr}")

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 2222))
    sock.listen(5)
    print("🤖 [MockDevice] 监听 2222 (支持命令回显)...")
    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()