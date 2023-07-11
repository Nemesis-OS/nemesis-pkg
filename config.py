"""Config file for Nemesis package manager."""
ANSI_CODES = ["\x1b[31m", "\x1b[32m", "\x1b[33m", "\x1b[34m", "\x1b[0m"]

REPOS = [
    [
        "https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST",
        "release.PKGLIST",
        "release",
        "https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/",
    ],
    [
        "https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST",
        "security.PKGLIST",
        "security-updates",
        "https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/",
    ],
]

CHECK_NECESSARY_FILES = True

PRESERVE_BUILD_FILES = True

CPU_FLAGS = []  # insert cpu flags here..
