import subprocess
import sys

subprocess.call("echo \"\" > out1.txt; echo \"\" > err1.txt; echo \"\" > out2.txt; echo \"\" > err2.txt", shell=True)

exe = sys.argv[1]
for i in range(1,21):
    s = '"#---------------------\n# Problem %d"' % (i)
    if i < 17:
        cmd = "echo %s >> out1.txt; echo %s >> err1.txt; python3.3 %s test%s.ml >> out1.txt 2>> err1.txt" % (s,s,exe, str(i));
        subprocess.call(cmd, shell=True)

    cmd = "echo %s >> out2.txt; echo %s >> err2.txt; python3.3 %s test%s.ml >> out2.txt 2>> err2.txt" % (s,s,exe, str(i) + "b");
    subprocess.call(cmd, shell=True)
