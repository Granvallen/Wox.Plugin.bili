Dim ws
Set ws = CreateObject("WScript.Shell")
rem msgbox WScript.Arguments(0)
ws.run "cmd /c start chrome " + WScript.Arguments(0),0
Wscript.Sleep 3500
ws.SendKeys "f"
Wscript.Sleep 1000
ws.SendKeys " "