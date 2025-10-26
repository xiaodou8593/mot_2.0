GetCurrentDir() {
    ; 获取当前活动窗口的进程和ID
    WinGet, activeProcess, ProcessName, A
    WinGetClass, activeClass, A
    currentDir := ""

    ; 尝试获取目录：针对不同类型的窗口进行处理
    if (activeProcess = "explorer.exe") ; 是资源管理器窗口
    {
        ; 使用COM对象获取Explorer路径
        for window in ComObjCreate("Shell.Application").Windows
        {
            try if (window.hwnd && window.hwnd = WinExist("A"))
            {
                currentDir := window.Document.Folder.Self.Path
                break
            }
        }
    }
    else
    {
        WinGetTitle, title, A
        if (RegExMatch(title, "O)([A-Z]:[\\/][^:\]]+)", match))
            currentDir := match.1
        else
            currentDir := "reg match error"
    }
    return currentDir
}