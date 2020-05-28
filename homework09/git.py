import hashlib
import sys
import os
import pathlib
import zlib
import io
import getpass


def object_read(sha):
	"""
	Reading a file in sha encoding
	and the return of the body
	"""
	gitdir = pathlib.Path(".git")
	path = gitdir / "objects" / sha[:2] / sha[2:]

	with open(path,mode="rb") as f:
		data = zlib.decompress(f.read())

	temp1 = data.find(b' ')
	obj_type = data[:temp1]
	temp2 = data.find(b'\x00',temp1)
	size = int(data[temp1:temp2].decode("ascii"))
	if size != len(data)-temp2-1:
		raise Exception(f"Object {sha} doesn't contain size")

	return data[temp2+1:]

def ls_tree(sha):
	"""
	output of tree objects
	"""
	data = object_read(sha)
	tree = tree_parse(data)
	for obj in tree:
		print(obj.decode("ascii"))

def tree_parse_one(raw,start):
	space = raw.find(b' ',start)
	mode = raw[start:space]
	null = raw.find(b'\x00',space)
	path = raw[space+1:null]
	return null+41, path

def tree_parse(raw):
	pos = 0 
	full = len(raw)
	res=[]
	while pos<full:
		pos,data = tree_parse_one(raw,pos)
		res.append(data)
	return res

def write_tree(dirname="."):
	"""
	Write a tree object from the current index
	"""
	w_tree=[]
	expel = [".git"]
	for route, folders, files in os.walk(dirname,topdown=True):
		folders[:] = [f for f in folders if f not in expel]
		for file in files:
			path = pathlib.Path(route) / file

			st = os.stat(path)
			filename = path.name
			mode_path = f"{st.st_mode:0} {filename}".encode()
			sha1 = object_sha(open(path,mode='rb'))
			tree_entry = mode_path + b"\x00" + sha1.encode()
			w_tree.append(tree_entry)

	print(w_tree)
	obj = io.BytesIO(b"".join(w_tree))
	sha = hash_object(obj, b'tree')
	print(sha)

def cat_file(sha):
	data = object_read(sha)
	print(data.decode("ascii"),end="")

def write_data(sha,result):
	gitdir = pathlib.Path(".git")
	path = gitdir / "objects" / sha[:2] / sha[2:]
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, mode = "wb") as f:
		f.write(zlib.compress(result))
	return

def check_obj():
	objects=[]
	dirname = pathlib.Path(".git/objects")
	for route, folders, files in os.walk(dirname,topdown=True):
		if len(route.split('/'))==3:
			route = route.split('/')
			print(route,' ' ,files) 
			object1=route[2]+files[0]
			objects.append(object1)
	return objects

	
def commit_files(dirname='.'):
	full_hashs = check_obj()
	print(full_hashs)
	result=[]
	for obj in full_hashs:
		print(obj)
		data = object_read(obj)
		for route, folders, files in os.walk(dirname,topdown=True):
			if len(route.split('.git'))==1:
				for file in files:
					path = pathlib.Path(route) / file
					with open(path, mode="rb") as f:
						data1=f.read()
					if data == data1:
						st = os.stat(path)
						filename = path.name
						temp1=(st.st_mode,obj,filename)
						result.append(temp1)
	data=b''
	for direct, sha, name in result:
		data += str(direct).encode() + b' ' + str(sha).encode() + b' ' +str(name).encode()+b'\n'

	answer = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data
	sha1 = hashlib.sha1(answer).hexdigest()
	write_data(sha=sha1,result=answer)
	return sha1


def commit_tree(massage,parent = None):
	gitdir = pathlib.Path(".git")
	path = gitdir / "logs" / "HEAD"

	if os.path.exists(path) == False:
		sha = commit_files()
		data = b'tree' + b' ' + str(sha).encode()+ b' ' + b'\n'
		data += b'author'+ b' ' + str(getpass.getuser()).encode() + b' '+ b'\n\n'
		data += str(massage).encode()+b' ' + b'\n'
		result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data
		sha1 = hashlib.sha1(result).hexdigest()
		write_data(sha=sha1,result=result)
		return sha1
	else:
		check_obj()
		sha = commit_files()
		data = b'tree' + b' ' + str(sha).encode()+b' ' + b'\n'
		data += b'parent'+b' ' + str(parent).encode()+b' '+b'\n'
		data += b'author'+ b' ' + str(getpass.getuser()).encode() + b' ' + b'\n\n'
		data += str(massage).encode()+b' ' + b'\n'
		result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data
		sha1 = hashlib.sha1(result).hexdigest()
		write_data(sha=sha1,result=result)
		return sha1



def commit(massage):
	gitdir = pathlib.Path(".git")
	path = gitdir / "COMMIT_EDITMSG"
	with open(path,mode = 'w') as f:
		f.write(f"{massage}\n")
	path = gitdir / "logs" / "HEAD"

	if os.path.exists(path) == False:
		sha = commit_tree(massage=massage)
		result = str('0'*40).encode() + b' ' + str(sha).encode()+ b' '+ str(getpass.getuser()).encode()+b' '
		result+=str(f'commit (initial): {massage}\n').encode()
		with open(path, mode = "wb") as f:
			f.write(result)
	else:
		f = open(path, mode = "rb")
		last_line = f.readlines()[-1].decode()
		temp1 = last_line.find(f' ')
		temp2 = last_line.find(f' ',temp1+1)
		parent = last_line[temp1+1:temp2]
		sha = commit_tree(massage=massage,parent=parent)

		result = str(parent).encode() + b' '+ str(sha).encode() + b' '+ str(getpass.getuser()).encode()+b' '
		result += str(f'commit: {massage}\n').encode()
		with open(path, mode = "ab") as f:
			f.write(result)
		

def object_sha(fp):
	"""
	encryption in sha1
	"""
	data = fp.read()
	result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data
	sha1 = hashlib.sha1(result).hexdigest()
	return sha1

def hash_object(fp,obj_type=b'blob'):
	"""
	hashing an object and 
	adding it to the directory
	"""
	data = fp.read()
	result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data
	sha = hashlib.sha1(result).hexdigest()
	gitdir = pathlib.Path(".git")
	path = gitdir / "objects" / sha[:2] / sha[2:]
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, mode = "wb") as f:
		f.write(zlib.compress(result))
	return sha


def create_repo():
	"""
	Creates a repository with folders
	"""
	os.mkdir(".git")
	os.mkdir(".git/objects")
	os.mkdir(".git/refs")
	os.mkdir(".git/logs")
	os.mkdir(".git/refs/heads")
	os.mkdir(".git/refs/heads/master")
	with open(".git/HEAD","w") as f:
		f.write("ref: refs/heads/master\n")
	print("Initialized git directory")

def main():
	command = sys.argv[1]
	if command == "init":
		create_repo()
	elif command == "cat-file":
		sha = sys.argv[3]
		cat_file(sha)
	elif command == "hash-object":
		file = sys.argv[3]
		with open(file, mode="rb") as f:
			sha=hash_object(f)
		print(sha)
	elif command == "ls-tree":
		sha = sys.argv[3]
		ls_tree(sha)
	elif command == "write-tree":
		dirname = sys.argv[2]
		write_tree(dirname)
	elif command == "commit":
		massage = sys.argv[3]
		commit(massage)
	else:
		raise RuntimeError(f"Unknown command #{command}")
		
if __name__=="__main__":
	main()
