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