#NoEnv
#SingleInstance Force

sendToDir := A_AppData "\Microsoft\Windows\SendTo"
target := A_ScriptDir "\mot_sendto.ahk"
shortcut := sendToDir "\MOT.lnk"

FileCreateShortcut, %target%, %shortcut%, %A_ScriptDir%, , MOT
MsgBox, 64, MOT, "installed sendto"
ExitApp