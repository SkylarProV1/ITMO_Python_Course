def encrypt_vigenere(plaintext, keyword):
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    list(plaintext)
    list(keyword)
    answer=list()
    for i in range(1,len(plaintext)+1):
        if (ord(plaintext[i-1])>=ord('a')) & (ord(plaintext[i-1])<=ord('z')):
            if(ord(keyword[i%len(keyword)-1])>=ord('a')) & (ord(keyword[i%len(keyword)-1])<=ord('z')):
                answer+=chr((ord(plaintext[i-1])-ord('a')+ord(keyword[i%len(keyword)-1])-ord('a'))%26+ord('a'))

        if (ord(plaintext[i-1])>=ord('A')) & (ord(plaintext[i-1])<=ord('Z')):
            if(ord(keyword[i%len(keyword)-1])>=ord('A')) & (ord(keyword[i%len(keyword)-1])<=ord('Z')):
                answer+=chr((ord(plaintext[i-1])-ord('A')+ord(keyword[i%len(keyword)-1])-ord('A'))%26+ord('A'))

        elif not ((ord('A')<=ord(plaintext[i-1])<=ord('Z')) or (ord('a')<=ord(plaintext[i-1])<=ord('z'))):
            answer+=plaintext[i-1]
    ciphertext=''.join(answer)
    return ciphertext


def decrypt_vigenere(ciphertext, keyword):
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    list(ciphertext)
    list(keyword)
    answer=list()
    for i in range(1,len(ciphertext)+1):
        if (ord(ciphertext[i-1])>=ord('a')) & (ord(ciphertext[i-1])<=ord('z')):
            if(ord(keyword[i%len(keyword)-1])>=ord('a')) & (ord(keyword[i%len(keyword)-1])<=ord('z')):
                answer+=chr((ord(ciphertext[i-1])-ord(keyword[i%len(keyword)-1]))%26+ord('a'))

        if (ord(ciphertext[i-1])>=ord('A')) & (ord(ciphertext[i-1])<=ord('Z')):
            if(ord(keyword[i%len(keyword)-1])>=ord('A')) & (ord(keyword[i%len(keyword)-1])<=ord('Z')):
                answer+=chr((ord(ciphertext[i-1])-ord(keyword[i%len(keyword)-1]))%26+ord('A'))

        elif not ((ord('A')<=ord(ciphertext[i-1])<=ord('Z')) or (ord('a')<=ord(ciphertext[i-1])<=ord('z'))):
            answer+=ciphertext[i-1]

    plaintext=''.join(answer)
    return plaintext