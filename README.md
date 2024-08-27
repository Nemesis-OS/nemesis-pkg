# nemesis-pkg
A fast and simple package manager for Nemesis inspired from `kiss` and `pacman`. This is completely written from scratch in pure python with no pip needed...

# usage:-
`nemsis-pkg` has various flags that performs operations and some operations have their args.

- [x] `sync` flag to sync the package database
- [x] `log` flag to see the total operations performed by `nemesis-pkg`
- [x] `list` flag can see what packages are in the repositories
- [x] `search` flag can search what packages are there..
- [ ] `install` flag can be used to install a package[needs some stuff to be added]
- [ ] `uninstall` flag can be used to uninstall a package[needs some testing]

### depreciations:
- [x] `history` its pretty much like logs and logs are way simpler and minimal[DEPRECIATED as of build 23625]

# huge thanks:-
- [`kiss`](https://github.com/kisslinux/kiss) - for its simplicity/user friendliness
- [`pacman`](gitlab.archlinux.org/pacman/pacman) - for its search implementation
- [`nala`](https://github.com/volitank/nala) - for the log idea

# NOTE: nemesis-pkg in python will no longer be used as a new npkg is being made in Lua(faster and better)
# SOURCE: https://git.sr.ht/~abrik1/nemesis-pkg
