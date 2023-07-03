#=====================================================
#genconfig-npkg: a tool to generate nemesis-pkg config|
#=====================================================

from subprocess import check_output

cpu_flags = check_output('lscpu').decode('utf-8').splitlines()[19].split()
cpu_flags.pop(0)
