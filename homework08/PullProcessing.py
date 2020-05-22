import os 
import sys
import numpy as np


class ProcessPool:
	
	def __init__(self,min_workers: int = 1,
				 max_workers: tp.Optional[int] = None,
				 mem_usage: tp.Optional[str] = None) -> None:
		self.min_workers = min_workers
		self.max_workers = max_workers or os.cpu_count()
		self.mem_usage = self.parse_mem_string(mem_usage)

	def parse_mem_string(self) -> int:
		pass

	def map(self,f:tp.Callable, data: tp.List[tp.Any]):
		pass


def heavy_computation(data_chunk):

	""" Data_Chunk has form set the first item is array
		a and second array b
	"""
	for matrixs in data_chunk:
		try:
			ma = np.matrix(matrixs[0])
			mb = np.matrix(matrixs[1])
			mc=ma*mb
		except Exception as e :
			print(e)


if __name__=="__main__":

	pool = ProcessPool(min_workers=2, max_workers=10, mem_usage='1Gb')
	results = pool.map(heavy_computation, big_data)