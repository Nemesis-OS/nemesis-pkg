# npkg-query: package searcher for nemesis-pkg

# TODO:
# - [ ] list packages installed
# - [ ] search packages
# - [ ] in search show what pkgs are out of date

version = 0.1

require "colorize"
require "json"

# colors
Colorize.enabled = Colorize.on_tty_only!()

# arguement parser
begin
    if ARGV[0] == "version" || ARGV[0] == "v"
        puts "=> npkg-query #{version}"
        puts "=> built by Crystal #{Crystal::VERSION} for #{Crystal::HOST_TRIPLE}"
    elsif ARGV[0] == "help" || ARGV[0] == "h"
        puts "=> npkg-query [#{"h,l,s,v".colorize(:magenta)}] {..}"
        puts "subcommands:".colorize.underline
        puts "  {#{"h".colorize(:light_magenta)}}#{"elp".colorize.bold}\t show this page"
        puts "  {#{"l".colorize(:light_magenta)}}#{"ist".colorize.bold}\t list installed pkgs"
        puts "  {#{"s".colorize(:light_magenta)}}#{"each".colorize.bold}\t search the specified pkg"
        puts "  {#{"v".colorize(:light_magenta)}}#{"ersion".colorize.bold}\t show the current version"
        puts "examples:".colorize.underline
        puts "=> #{"note".colorize(:light_magenta)}: subcommands in #{"yellow".colorize(:light_yellow)}, args in #{"red".colorize(:light_red)} and comments in #{"blue".colorize(:light_blue)}"
        puts "  $ npkg-query #{"search".colorize(:light_yellow)} #{"firefox".colorize(:light_red)} #{"# searching pkgs similar to firefox".colorize(:light_blue)}"
        puts "  $ npkg-query #{"list".colorize(:light_yellow)} #{"# finding which packages are installed".colorize(:light_blue)}"
    else
        unless ARGV[0] == nil
            puts "=> #{"error:".colorize(:light_red)} available args are #{["help", "list", "search", "version"].colorize(:magenta)}"
        else
            puts "=> #{"error:".colorize(:light_red)} no arg specified"
        end
        Process.exit(1)
    end
rescue
    puts "=> #{"error:".colorize(:light_red)} some error occured."
    Process.exit(1)
end
