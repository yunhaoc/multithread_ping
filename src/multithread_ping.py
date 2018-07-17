#说明：本代码默认是ping：127.0.0.1 100s；ping：127.0.0.1 200s
#如果需要改变ip和ping的时间，只需要在运行该程序时带上参数既可，参数形式如下：
#python Multithread_Ping ip 时间 ip 时间
#coding:utf-8

import subprocess
import threading
import os
import signal
import time
import sys

openFd = []
threads = []
#设置默认的参数
argsList = [{'ipAddr':'127.0.0.1','time':5,'pid':0,'log':[]},
			{'ipAddr':'127.0.0.1','time':10,'pid':0,'log':[]}]

#计算argsList长度
length = len(argsList)
#获取输入参数
args = sys.argv
argsNum = (len(args) - 1) %2
argsHalf = int((len(args) - 1)/2)
if argsNum == 0:
	for i in range(0,argsHalf):
#		print(i)
		argsList[i]['ipAddr'] = args[2*i + 1]
		try:
			argsList[i]['time'] = int(args[2*i + 2])	
		except ValueError:
			 print("input time value error!")
	

#到设定时间之后发送SIGINT信号杀死线程
def fun_timer(pid):
	try:
		os.kill(pid ,signal.SIGINT)
	except OSError:
		print("kill args error")

#运行ping命令并将线程pid保存到pidList中
def subProcess(ipAddr):
	cmd = "ping " + ipAddr + " " + "-t"
	cmd_list = cmd.split(" ")
	sub = subprocess.Popen(cmd_list,stdout = subprocess.PIPE)
	openFd.append(sub)
	logList = []
	for i in range(0,length):
		if ipAddr == argsList[i]['ipAddr']:
			argsList[i]['pid'] = sub.pid
			#启动定时器
			timer = threading.Timer(argsList[i]['time'],fun_timer,(argsList[i]['pid'],))
			timer.start()

			for line in iter(sub.stdout.readline,''):
				if not len(line):
					break
				if len(line) == 2:
					continue
				argsList[i]['log'].append(line.decode('GBK'))
				print(line.decode('GBK'))

	
#主函数创建并启动线程	
def main():
	for i in range(0,2):
		threadn = threading.Thread(target=subProcess,args=(argsList[i]['ipAddr'],))
		threads.append(threadn)
		
	for thread in threads:
		thread.setDaemon(True)
		thread.start()

	thread.join()

if __name__ == '__main__':
	logList = []
	logList1 = []

	main()
	for index in range(0,2):
		haveAccept =0
		haveSend = 0
		haveLose = 0;
		haveSend = len(argsList[index]['log']) - 1
#		print(argsList[index]['log'])
		for i in range(1,len(argsList[index]['log'])):
#			print(argsList[index]['log'][i])
			loc = argsList[index]['log'][i].find('TTL')
			if loc != -1:
				haveAccept = haveAccept + 1
		
		haveLose = haveSend - haveAccept
		countInfo = '%s%d%s%d%s%d' % ('数据包：已发送 = ',haveSend,' ,已接收 = ',haveAccept,' ,丢失 = ',haveLose)
		countInform = countInfo + ' ({:.0%}'.format(haveLose/haveSend) + ' 丢失)'
		argsList[index]['log'].append(countInform)
		print(argsList[index]['log'])
#		print(argsList)
