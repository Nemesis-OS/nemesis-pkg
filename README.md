# nemesis-pkg
A fast and simple package manager for Nemesis inspired from `kiss` and `pacman`. This is completely written from scratch...

# usage:-
`nemsis-pkg` has various flags that performs operations and some operations have their args.

- `i` flag installs a package... `nemesis-pkg i {pkg1} {pkg2}`
- `r` flag removes a package... `nemesis-pkg r {pkg1} {pkg2}`
- `lsi` flag list system installed packages.. `nemesis-pkg lsi {pkg1} {pkg2}`
- `lri` flag list packages present in repo.. `nemesis-pkg lri {pkg1} {pkg2}`
- `ug` flag updates packages to latest version.. `nemesis-pkg ug`
- `ud` flag updates the package database... `nemesis-pkg ud`
- `h` shows info on flags and usage.. `nemesis-pkg h`
- `v` flag shows the version of `nemesis-pkg`.. `nemesis-pkg v`

# huge thanks:-
- [`kiss`](https://github.com/kisslinux/kiss)
- [`pacman`](gitlab.archlinux.org/pacman/pacman)
