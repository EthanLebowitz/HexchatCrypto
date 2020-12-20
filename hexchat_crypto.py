__module_name__ = "crypto"
__module_version__ = "1.0"
__module_description__ = "a cryptographic implementation for hexchat"

import irccrypt
import hexchat

escapeCharacter="\\"
userNickColor="\00304"
encryptedTextColor="\00303"
decryptedTextColor=""
info = {"key":"None", "secret":"None", "private":"None"}
hooks = {"sendHook":"None", "recHook":"None", "commandHook":"None", "exchangeHook":"None"}

def initiateExchange(nickname):#initiate key exchange
	private = irccrypt.DH1080Ctx()
	hexchat.command("PRIVMSG "+nickname+" :"+irccrypt.dh1080_pack(private))
	info["private"] = private
	return hexchat.EAT_HEXCHAT
	
def finishExchange(word, word_eol, userdata):#receive exchange requests or responses
	nickname = word_eol[0].split("!")[0][1:]
	if word[3][2:] == "DH1080_INIT": #if it's an initiation
		private = irccrypt.DH1080Ctx()
		public = word_eol[3][2:]
		irccrypt.dh1080_unpack(public, private)
		hexchat.command("PRIVMSG "+nickname+" :"+irccrypt.dh1080_pack(private)) #respond
		secret = irccrypt.dh1080_secret(private)
		print "key exchange complete with "+nickname+": "+secret
		info["secret"] = secret
		return hexchat.EAT_HEXCHAT
	elif word[3][2:] == "DH1080_FINISH": #if it's a response
		public = word_eol[3][2:]
		private = info["private"]
		irccrypt.dh1080_unpack(public, private)
		secret = irccrypt.dh1080_secret(private)
		print "key exchange complete with "+nickname+": "+secret
		info["secret"] = secret
		return hexchat.EAT_HEXCHAT

def crypto(plainText, direction):
	key = irccrypt.BlowfishCBC(info["key"])
	if direction == "e":
		cipherText = irccrypt.mircryption_cbc_pack(plainText, key)
	if direction == "d":
		cipherText = irccrypt.mircryption_cbc_unpack(plainText, key)
	return cipherText
		
def sendFilter(word, word_eol, userdata):
	channel = hexchat.get_info("channel")#get channel to privmsg
	if word_eol[0][:3]!="+OK" and word_eol[0][:1]!="\\":#if it isn't your new encrypted one or an escaped one
		hexchat.emit_print("Channel Message", userNickColor + hexchat.get_info("nick"), encryptedTextColor + word_eol[0])#makes it look to you like you spoke in plain text
		hexchat.command("PRIVMSG "+channel+" :"+crypto(word_eol[0], "e"))#encrypt it
	if word_eol[0][:1]==escapeCharacter:#if it's escaped
		hexchat.emit_print("Channel Message", userNickColor + hexchat.get_info("nick"), word_eol[0][1:])#prints it with a stripped \
		endCrypto()#makes the sendFilter hook not catch it
		hexchat.command("PRIVMSG "+channel+" :"+word_eol[0][1:])#dont encrypt it
		beginCrypto()
	return hexchat.EAT_HEXCHAT

def recFilter(word, word_eol, userdata):
	if word_eol[3][2:5]=="+OK":#if encrypted
		hexchat.emit_print("Channel Message", word_eol[0].split("!")[0][1:], encryptedTextColor + crypto(word_eol[3][2:], "d"))#decrypt it
		return hexchat.EAT_HEXCHAT
	else:#otherwise do nothing
		return hexchat.EAT_NONE
		
def endCrypto():
	hexchat.unhook(hooks["sendHook"])
	hooks["sendHook"] = "None"
	hexchat.unhook(hooks["recHook"])
	hooks["recHook"] = "None"
		
def beginCrypto():
	if hooks["sendHook"]=="None":
		hooks["sendHook"] = hexchat.hook_command("", sendFilter)
		hooks["recHook"] = hexchat.hook_server("PRIVMSG", recFilter)
	else:
		hexchat.emit_print("\00304Your chat is already encrypted.")
		
def switch(word, word_eol, userdata):
	if len(word)>1:
		if word[1]=="on":
			try:
				info["key"] = word[2]
				beginCrypto()
				print "encryption on"
			except:
				print "Usage: /crypt on <key>" 
		elif word[1]=="off":
			endCrypto()
		elif word[1]=="exchange":
			initiateExchange(word[2])
		elif word[1]=="setkey":
			try:
				info["key"] = word[2]
				print "key set to: " + info["key"]
			except:
				print "Usage: /crypt setkey <new key>"
		else:
			hexchat.emit_print("\00304Command not recognised: " + word_eol[1])
	else:
		print "Usage: /crypt on <key>" 
	return hexchat.EAT_HEXCHAT
	
hooks["commandHook"] = hexchat.hook_command("crypt", switch)
hooks["exchangeHook"] = hexchat.hook_server("PRIVMSG", finishExchange)