import subprocess
processes = [subprocess.Popen(program) for program in ['python daemonSender.py', 'python daemonReceiver.py']]
for process in processes:
    process.wait()