def encrypt_caesar(plaintext):
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    list(plaintext)
    answer=list()
    for i in range(0,len(plaintext)):
        if (ord(plaintext[i])>=ord('a')) & (ord(plaintext[i])<=ord('z')):
            answer+=chr((ord(plaintext[i])-ord('a')+3) % 26+ord('a'))
        if (ord(plaintext[i])>=ord('A')) & (ord(plaintext[i])<=ord('Z')):
            answer+=chr((ord(plaintext[i])-ord('A')+3) % 26+ord('A'))
        elif  not ((ord('A')<=ord(plaintext[i])<=ord('Z')) or (ord('a')<=ord(plaintext[i])<=ord('z'))):
            answer+=plaintext[i]
    ciphertext=''.join(answer)
    return ciphertext


def decrypt_caesar(ciphertext):
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    list(ciphertext)
    answer=list()
    for i in range(0,len(ciphertext)):
        if (ord(ciphertext[i])>=ord('a')) & (ord(ciphertext[i])<=ord('z')):
            answer+=chr((ord(ciphertext[i])-ord('a')-3) % 26+ord('a'))
        if (ord(ciphertext[i])>=ord('A')) & (ord(ciphertext[i])<=ord('Z')):
            answer+=chr((ord(ciphertext[i])-ord('A')-3) % 26+ord('A'))
        elif not ((ord('A')<=ord(ciphertext[i])<=ord('Z')) or (ord('a')<=ord(ciphertext[i])<=ord('z'))):
            answer+=ciphertext[i]
    plaintext=''.join(answer)
    return plaintext