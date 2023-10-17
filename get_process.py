import psutil,os,signal


def get_process_by_name_port(process_name, port):
    processes = [proc for proc in psutil.process_iter() if proc.name()
                 == process_name]
    for p in processes:
        for c in p.connections():
            if c.status == 'LISTEN' and c.laddr.port == port:
                return p
    return None

def stop_process(process_name, port):
    process_python_8080 = get_process_by_name_port(process_name, port)
    try:
        print("PID", process_python_8080.pid)
        os.kill(process_python_8080.pid,signal.SIGKILL)
    except:
        print('no running process')