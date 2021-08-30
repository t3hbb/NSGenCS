# Troubleshooting

With all of the varied .NET installation combinations which can cause issues, here are some troubleshooting steps for some of the more common problems as they crop up :

1. Initial `Build failed`

![image](https://user-images.githubusercontent.com/21687763/131313727-f4c4b6cb-8704-448b-a17e-c5420007d3d9.png)

Re-run the command line with `-noclean true` and look at the file `output.shellcode` in your shellcode directory (default is `ShellcodeTemplate`). This should contain the error message from the dotnet publish command. I have updated the ShellcodeTemplate to use net45 instead of netcoreapp3.1 to help prevent these errors but just in case it still occurs for you, here's where to look.


