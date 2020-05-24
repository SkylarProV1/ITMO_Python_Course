import os 
import psutil
import numpy as np
from multiprocessing import Queue, Process
from threading import Thread
import time
import typing as tp
import random

class ProcessPool:
	
	def __init__(self,min_workers: int = 1,
				 max_workers: tp.Optional[int] = None,
				 mem_usage: tp.Optional[str] = None) -> None:
		if min_workers > 0:
			self.min_workers = min_workers
		else: 
			raise ValueError("Min workers should be > 0")
		self.max_workers = max_workers or (os.cpu_count())
		if self.min_workers > self.max_workers:
			raise ValueError("Min workers shouldn't be > Max workers")
		self.mem_usage = self.parse_mem_string(mem_usage)
		self.results=list()
		self.comupte_size=2.**30
		self.check_monitor=0

	def parse_mem_string(self,mem_usage) -> int:
		sizes={'gb':1,'mb':2.**10}
		value=''
		type_mem=''
		for mem in mem_usage:
			try:
				int(mem)
				value+=mem
			except ValueError:
				type_mem+=mem.lower()
				continue
		if sizes.get(type_mem) == None:
			raise ValueError("You use GB or MB")
		elif float(value)!=0:
			print(float(value))
			print(float(value)/sizes.get(type_mem))
			return float(value)/sizes.get(type_mem)
		else:
			raise ValueError("You didn't use mem")


	def map(self,f:tp.Callable, data: tp.List[tp.Any]):

		len_data=len(data)
		self.chunksize=len_data*(1/(os.cpu_count()))

		self.worker_processes(data=data,func=f,len_data=len_data)
		return self.results

	def explorer_worker(self,data,func,queue_in,queue_out):

		queue_in.put(data[:int(self.chunksize)])
		process = Process(target=func,args = (queue_in,queue_out,))
		controler = Thread(target = self.test_monitor, args = (process,), daemon = True)
		process.start()
		controler.start()

		self.results.append(queue_out.get())
		vector_mem=self.control_data.get()
		process.terminate()
		return vector_mem

	def regenerator_worker(self,data,func,queue_in,queue_out,chunksizes) -> None:

		kills=list()
		gap_restart=list()
		if self.check_monitor >0:
			#print(self.check_monitor)
			#print(f"Main process comlited {self.check_monitor}")
			for _ in range(self.check_monitor):
				kill=self.control_data.get()
				if len(kill) > 0 :
					kills.append(kill)
		for kill in kills:
			temp=[chunksizes[j][1] for j in range(len(chunksizes)) if len(kill) >0  and chunksizes[j][0] == kill[0]]
			gap_restart.append(temp[0])
		#print(gap_restart)

		processes2 = list()
		if len(kills)>0:
			#print(f"Pull processes {processes}")
			#print(f"I reload1")
			#print(f"Count {gap_restart} ")
			for gap in gap_restart:
				#print(f"I reload2 {gap}")
				queue_in.put(data[int(gap[0]):int(gap[1])])
				process = Process(target=func,
				args = (queue_in,queue_out))
				process.start()
				processes2.append(process)

			if len(gap_restart)>0:

				for _ in range(len(gap_restart)):
					self.results.append(queue_out.get())

				for p in processes2:
					p.terminate()

	def worker_processes(self,data,func,len_data,):

		queue_in = Queue()
		queue_out = Queue()
		self.control_data = Queue()

		vector_mem=self.explorer_worker(data=data,func=func,queue_in=queue_in,
						queue_out=queue_out,)
		if len(vector_mem)==0:
			limit = self.max_workers 
		else:
			self.max_mem=max(vector_mem)
			limit=min(int(self.mem_usage/self.max_mem),self.max_workers)
		if limit < self.min_workers:
			raise ValueError("You have set the min worker threshold too large for allocated memory")

		print(len(data))

		#print(f"Max count process {limit}")
		#print(f"Max mem in first runner {self.max_mem}")
		processes = list()
		chunksizes = list()
		treatment=len_data-self.chunksize
		for i in range(limit):
			gap=int(self.chunksize+(treatment/limit)*i),int(self.chunksize+(treatment/limit)*(i+1))
			queue_in.put(data[int(gap[0]):int(gap[1])])
			process = Process(target=func,
				args = (queue_in,queue_out,))
			process.start()
			temp=process.pid,gap
			chunksizes.append(temp)
			processes.append(process)

		if len(processes)!=0:
			controler = Thread(target = self.main_monitor,args = (processes,), daemon = True)
			controler.start()

		for process in processes:
			print(process)
			if process.is_alive():
				py = psutil.Process(process.pid)
				if py.status()!='zombie':
					self.results.append(queue_out.get())

		for p in processes:
			p.terminate()

		self.regenerator_worker(data=data,func=func,queue_in=queue_in,
					queue_out=queue_out,chunksizes=chunksizes)


	def test_monitor(self,process, time_check: int = 0.1,):
		timing = time.time()
		mem_data=list()
		while process.is_alive():
			if time.time() - timing > time_check:
				timing = time.time()
				py = psutil.Process(process.pid)
				memoryUse = py.memory_info().rss / self.comupte_size
				mem_data.append(memoryUse)
		self.control_data.put(mem_data)

	def main_monitor(self,processes, time_check: int=0.5):
		timing = time.time()
		while True:
			if time.time() - timing > time_check:
				mem_proceses = {process.pid: -1 for process in processes}

				count=0
				for process in processes:
					if not process.is_alive():
						print(f"Finish: {process.pid}!")
						count+=1
				if count == len(processes):
					print("Break with main_monitor")
					break

				timing = time.time()
				full_mem_compute=0
				for process in processes:
					if process.is_alive():
						py = psutil.Process(process.pid)
						if py.status()!='zombie': 
							memoryUse = py.memory_info().rss / self.comupte_size
							mem_proceses[process.pid] = memoryUse
							full_mem_compute+=memoryUse
							print(f"Process: {process.pid} Memory: {memoryUse}")

				self.check_monitor+=1
				kills=list()
				while full_mem_compute > self.mem_usage:
					max_mem = max(mem_proceses.values())
					help_list = list(mem_proceses.items())
					pid = [help_list[i][0] for i in range(len(help_list)) if help_list[i][1] == max_mem]
					pid=pid[0]
					if psutil.pid_exists(pid):
						py = psutil.Process(pid)
						py.kill()
						mem_proceses.pop(pid)
						kills.append(pid)
						full_mem_compute-=max_mem
				self.control_data.put(kills)
				print(f"kills thisis big process: {kills}")

def heavy_computation(queue_in,queue_out):
	""" 
	Data_Chunk has form set the first item 
	is array a and second array b
	"""
	results=list()
	data_chunk=queue_in.get()
	for matrixs in data_chunk:
		ma = np.matrix(matrixs[0])
		mb = np.matrix(matrixs[1])
		mc=ma*mb
		results.append(mc)
	if len(data_chunk)==len(results):
		queue_out.put(results)

def generation_big_data():

	fullsteck = list()
	for l in range(10000):
		if l < 3000:
			M=20
			N=20
		else:
			N=100
			M=100
		matrixs=([[ i for i in range(M)] for j in range(N) ],[[ i for i in range(N)] for j in range(M) ])
		fullsteck.append(matrixs)
	print("Form data")
	return fullsteck

if __name__=="__main__":
	big_data = generation_big_data()
	pool = ProcessPool(min_workers=1, max_workers=10, mem_usage='3000Mb')
	T1 = time.time()
	results = pool.map(heavy_computation, big_data)
	T2 = time.time()

	print(T2-T1)
	print(len(results))
	summ=0
	for i in results:
		summ+=len(i)
	print("Matrix: ",summ)
