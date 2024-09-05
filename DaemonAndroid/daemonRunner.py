import subprocess
processes = [subprocess.Popen(program) for program in ['/data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/Tushkey/DaemonAndroid/daemonSender.py', '/data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/Tushkey/DaemonAndroid/daemonReceiver.py']]
for process in processes:
    process.wait()