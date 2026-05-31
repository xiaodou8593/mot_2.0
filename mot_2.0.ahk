#Include %A_ScriptDir%\mylib.ahk

^p::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\create_datapack.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^m::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\memory_stack.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^o::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\create_mcfo.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^t::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\create_mot.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^u::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\.mot.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^i::
	currentDir := GetCurrentDir()
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\print_plates.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%", %currentDir%, UseErrorLevel, OutputVarPID
	if (ErrorLevel = "ERROR")
		MsgBox, 运行Python脚本失败！请检查工作目录"%currentDir%"是否存在。
	return

^\::
	pythonPath := "python" ; 假设已在系统PATH中，否则需完整路径如 "C:\Python39\python.exe"
	pythonScript := A_ScriptDir "\opener_gui.py"
	RunWait, %pythonPath% "%pythonScript%" "%A_ScriptDir%"
	return