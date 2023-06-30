ANSI_CODES = [
    "\x1b[31m",
    "\x1b[32m",
    "\x1b[33m",
    "\x1b[34m",
    "\x1b[0m"
]

REPOS = [
    ["https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST" , "release.PKGLIST" , "release" , "https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/"],
    ["https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST" , "security.PKGLIST" , "security-updates" , "https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/"]
]

check_nessary_files = True

preserve_build_files = True

cpu_flags = [] # insert cpu flags here..
