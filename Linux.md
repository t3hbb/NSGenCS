# .NET for Linux

.NET is supported on Linux through official Microsoft packages or manual installation. Installation instructions for supported operating systems and package management systems are available through the Microsoft .NET Core site.

General steps are as follows:

1) [Microsoft: Install .NET on Linux](https://docs.microsoft.com/en-us/dotnet/core/install/linux).  For example, instructions are listed for [Debian](https://docs.microsoft.com/en-us/dotnet/core/install/linux) as well as other Linux operating systems.

2) Install the SDK, making sure to complete any pre-installation steps such as removing previous versions, adding package management repositories and signing keys, dependencies, etc.

3) Make note of any instructions to install other .NET versions other than the latest versiopn. For example, Microsoft states for [Debian](https://docs.microsoft.com/en-us/dotnet/core/install/linux):

    > The packages added to package manager feeds are named in a hackable format, for example: {product}-{type}-{version}.
    >
    > ...
    > 
    > - version
    >
    > The version of the SDK or runtime to install. This article will always give the instructions for the latest supported version. Valid options are any released version, such as:
    > 
    > - 5.0
    > - 3.1
    > - 3.0
    > - 2.1
    >
    > ...
    >
    > Install the .NET Core 3.1 SDK: `dotnet-sdk-3.1`

4) Check installed .NET versions after installation is completed, for example:

    ```$``` ```dotnet --list-sdks```

    ```3.1.420 [/usr/share/dotnet/sdk]```


# Linux Support
The source has been minimally refactored to support Linux paths and file system operations. The tool will also create a backup of the original project file, for example, `Payload.csproj.orig` to avoid inadvertedly globbering it. 

The tool now supports the replacing the target framework moniker (TFM) within the templates SDK-style project files and is specifically hardcoded to look for `Payload.csproj`. This is implemented as an optional argument `-targetframework TFM`. By default, it will use `net45` to support the versions in the original template project files (backward compatibility). 

**The `net45` version will fail on Linux since it is not a supported .NET version on Linux.**

For Linux, simply use the `-targetframework` command line argument to align with the installed version. This will modify the specified template's `TargetVersion` tag. For example, `-targetframework netcoreapp3.1` will read `Payload.csproj.orig`, replace the string, then create a new version of `Payload.csproj` with the .NET Core 3.1 SDK string `netcoreapp3.1`. 

## Example

After installing .NET on Linux then executing `python3 nsgencs.py` with the proper arguments, an error will likely be thrown resembling the following:

```$``` ```python3 NSGenCS.py -file msgbox.cs -method xor -template Thread_Hijack -key 22```
```
...

> Creating encoded shellcode from CS file
> Generating payload
> Cleanup
Microsoft (R) Build Engine version 16.7.2+b60ddb6f4 for .NET
Copyright (C) Microsoft Corporation. All rights reserved.

  Determining projects to restore...
  Restored /home/user/NSGenCS/Thread_Hijack/Payload.csproj (in 92 ms).
/usr/share/dotnet/sdk/3.1.420/Microsoft.Common.CurrentVersion.targets(1177,5): error MSB3644: The reference assemblies for .NETFramework,Version=v4.5 were not found. To resolve this, install the Developer Pack (SDK/Targeting Pack) for this framework version or retarget your application. You can download .NET Framework Developer Packs at https://aka.ms/msbuild/developerpacks [/home/user/NSGenCS/Thread_Hijack/Payload.csproj]
```

In the above example, the .NET Core 3.1 SDK has been installed but `dotnet` is failing due to target version defined in the project file.

To resolve, use the `-targetframework`.

```$``` ```python3 NSGenCS.py -file msgbox.cs -method xor -template Thread_Hijack -key 22 -targetframework netcoreapp3.1```

```
...

> Creating encoded shellcode from CS file
> Generating payload
> Cleanup
Microsoft (R) Build Engine version 16.7.2+b60ddb6f4 for .NET
Copyright (C) Microsoft Corporation. All rights reserved.

  Determining projects to restore...
  Restored /home/user/NSGenCS/Thread_Hijack/Payload.csproj (in 141 ms).
  Payload -> /home/user/NSGenCS/Thread_Hijack/bin/Release/netcoreapp3.1/win10-x64/Payload.dll
  Payload -> /home/user/NSGenCS/Thread_Hijack/bin/Release/netcoreapp3.1/win10-x64/publish/

If you didn't see a bunch of red lines before this message, you should see payload.exe now :)
```

## Additional Information

More information on the TFMs can be found on Microsoft's site, [Target frameworks in SDK-style projects](https://docs.microsoft.com/en-us/dotnet/standard/frameworks).

More information on the the project file syntax can be found on Microsoft's site, [Target Framework Monikers define build time APIs](https://docs.microsoft.com/en-us/dotnet/core/versions/selection#target-framework-monikers-define-build-time-apis)