#NoEnv
#SingleInstance Off
SetWorkingDir %A_ScriptDir%

if (A_Args.Length() < 1) {
    MsgBox, 16, MOT, Please right-click a folder and use Send to > MOT.
    ExitApp
}

targetDir := A_Args[1]

if (!InStr(FileExist(targetDir), "D")) {
    MsgBox, 16, MOT, Not folder: %targetDir%
    ExitApp
}

Menu, MotMenu, Add, Create datapack, CreateDatapack
Menu, MotMenu, Add, Install MOT here, CreateMot
Menu, MotMenu, Add, Create .doc.mcfo, CreateMcfo
Menu, MotMenu, Add, Open memory stack, MemoryStack
Menu, MotMenu, Add, Run MOT sync, RunMot
Menu, MotMenu, Show
return

CreateDatapack:
    RunPython("create_datapack.py")
return

CreateMot:
    RunPython("create_mot.py")
return

CreateMcfo:
    RunPython("create_mcfo.py")
return

MemoryStack:
    RunPython("memory_stack.py")
return

RunMot:
    RunPython(".mot.py")
return

RunPython(scriptName) {
    global targetDir
    libPath := A_ScriptDir
    pythonPath := "python"
    scriptPath := libPath "\" scriptName
    RunWait, %ComSpec% /k ""%pythonPath%" "%scriptPath%" "%libPath%"", %targetDir%
}