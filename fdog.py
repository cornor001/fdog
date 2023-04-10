import os
import sys
import time
import logging
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler,FileSystemEventHandler

global bckp
bckp=False

if os.name=='posix':
	DEBUG=True
else:
	DEBUG=False

if DEBUG:
	path="/Users/hongwutang/school/"
else:
	path="D:\\"


class DirFileEventHandler(LoggingEventHandler,FileSystemEventHandler):
	def __init__(self, **kwargs):
		super(DirFileEventHandler, self).__init__(**kwargs)
		self._watch_path = path

	def on_any_event(self,event):
		file_path = event.src_path
		file_name = os.path.split(file_path)[-1]
		if(file_name=="wdog.log"):
			print("监测到日志文件操作，此次操作将汇报至管理员")
			f=open(f"{path}.admin.log","a")
			ntime=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
			f.write(f"[Warning] {ntime} - 日志文件变化\n")
			logging.critical("Log Change")
			f.close()
		else:
			pass


def watch(con1,con2):
	con2.close()
	print(f"Fdog监督进程启动 pid:{os.getpid()}")
	while 1:
		try:
			con1.recv()
		except EOFError:
			try:
				f=open(f"{path}close.config","r")
				if(f.read()=="sanfanadmin\n"):
					print("密钥正确，监督程序关闭")
					f=open(f"{path}.admin.log","a")
					ntime=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
					f.write(f"{ntime} - 通过密钥关闭程序\n")
					
					break
				else:
					print("密钥错误，此次操作将记录日志")
					f.close()
					f=open(f"{path}.admin.log","a")
					ntime=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
					f.write(f"{ntime} - 试图通过密钥关闭程序，密钥错误\n")
					
			except:
				pass
			p=multiprocessing.Process(target=fdog) 
			p.start()
			f=open(f"{path}.admin.log","a")
			ntime=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
			f.write(f"{ntime} - 试图关闭主程序\n") 
			print(f"主进程被杀，重新启动")
			
			break

def fdog():
	print(f"Fdog主进程启动 pid:{os.getpid()}")
	logging.basicConfig(filename = "wdog.log",
                    	filemode = "a",
						level=logging.INFO,
						format='%(asctime)s - %(message)s',
						datefmt='%Y-%m-%d %H:%M:%S')
	event_handler = DirFileEventHandler()
	observer = Observer()
	observer.schedule(event_handler,path,recursive=True)
	observer.start()
	con1,con2=multiprocessing.Pipe()
	wt=multiprocessing.Process(target=watch,args=(con1,con2))
	wt.start()
	con1.close()
	while True:

		try:
			con2.send("alive")
		except:
			f=open(f"{path}.admin.log","a")
			ntime=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
			f.write(f"{ntime} - 试图关闭监督程序\n")
			con1,con2=multiprocessing.Pipe()
			wt=multiprocessing.Process(target=watch,args=(con1,con2))
			wt.start()
			con1.close()
			
		time.sleep(1)




if __name__=="__main__":
	p=multiprocessing.Process(target=fdog)
	p.start()