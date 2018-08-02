# homework-ftp
python homework to ftp
功能：
FTP传输文件
1.用户加密认证
2.允许多个用户登陆
3.每个用户有自己的家目录，不能互相访问
4.对用户进行磁盘配额，可用空间不同
5.允许用户在ftp_server上随意切换目录
6.允许用户查看当前目录文件
7.允许用户上传下载文件，保证文件一致性
使用：
'\server\database\'下进入cmd，输入python account.py,添加账户
'\server\bin\'下进入cmd，输入python server.py,运行服务器
'\client\bin\'下进入cmd，输入python client.py,运行客户端
