import socket
import threading
import paramiko
import time

# --- 配置区 ---
HOST_KEY = paramiko.RSAKey.generate(2048)
PORT = 2222

# 定义命令回复 (Key必须小写)
# 定义命令回复 (Key必须小写)
RESPONSES = {
    "show version": "Cisco IOS Software, C2960 Software (C2960-LANBASEK9-M), Version 15.0(2)SE4\nSystem serial number: FOC12345678",
    
    # --- 核心修改：增加多种命令变体，指向同一个结果 ---
    "show ip int brief": "Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/1     192.168.1.1     YES manual up                    up\nGigabitEthernet0/2     unassigned      YES unset  down                  down",
    "show ip interface brief": "Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/1     192.168.1.1     YES manual up                    up\nGigabitEthernet0/2     unassigned      YES unset  down                  down",
    "show interfaces status": "Port      Name               Status       Vlan       Duplex  Speed Type\nGi0/1                        connected    1          a-full  a-100 10/100/1000BaseTX\nGi0/2                        notconnect   1          auto    auto 10/100/1000BaseTX",
    
    # --- 骗过初始化命令 ---
    "terminal": "", 
    "no logging": "",
}

class FakeSwitch(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED
    
    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_shell_request(self, channel):
        return True

def handle_connection(client_sock, addr):
    transport = paramiko.Transport(client_sock)
    transport.add_server_key(HOST_KEY)
    server = FakeSwitch()
    
    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None: return

        print(f"✅ [{addr}] 连接成功")
        
        # 模拟 Cisco 欢迎语和提示符
        chan.send("\r\nUser Access Verification\r\n\r\nSwitch>")
        
        while True:
            # 接收数据
            received = chan.recv(1024).decode('utf-8', errors='ignore')
            if not received: break
            
            # ★关键修复1：立即回显 (Echo) 欺骗 Netmiko
            # Netmiko 看到自己发的字回来了，才会继续往下走
            chan.send(received)

            # 简单的命令缓冲区处理 (等到收到换行符才执行)
            if '\n' in received or '\r' in received:
                cmd_buffer = received.strip()
                
                # 查找回复
                response = "" # 默认为空，模拟静默成功
                found = False
                
                # 也就是如果命令不是空的，我们才去查字典
                if cmd_buffer:
                    response = "% Unknown command."
                    for k, v in RESPONSES.items():
                        if k in cmd_buffer.lower():
                            response = v
                            found = True
                            break
                    # 如果是 terminal 命令，虽然查到了是空，但算找到
                    if not found and ("terminal" in cmd_buffer.lower() or "no logging" in cmd_buffer.lower()):
                         response = ""

                # 构造最终输出：换行 + 结果 + 换行 + 提示符
                # ★关键修复2：Cisco 严格要求 \r\n 换行
                if response:
                    output = f"\r\n{response}\r\nSwitch>"
                else:
                    output = "\r\nSwitch>"
                
                # 发送结果
                chan.send(output)
            
    except Exception as e:
        print(f"断开: {e}")
    finally:
        transport.close()
        client_sock.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', PORT))
    sock.listen(5)
    print(f"🚀 [终极版虚拟交换机] 监听端口: {PORT} (支持 Echo)")
    
    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_connection, args=(client, addr)).start()

if __name__ == "__main__":
    main()