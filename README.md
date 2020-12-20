## A cryptographic module for hexchat ##

/crypt on <key>              begins encrypting all output and decrypting all input with <key>. Uses mircryption (so it's CBC, horrah!)

\                            escapes a message so it isn't encrypted

/crypt off                   stops encrypting/decrypting

/crypt exchange <username>   uses Diffie-Hellman key exchange to create a shared key with <username>

All encrypted messages are displayed in green.

irccrypt.py must be moved/copied into HexChat's folder.
You also need pycryptodome or pycrypto (can both be installed through pip)

Just tested this module at the time of commit and something no longer works. This was my pride and joy back when I wrote it in 2016, so I hope to get it running again. 