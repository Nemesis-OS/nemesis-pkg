# npkg-query: package searcher for nemesis-pkg

# TODO:
# - [ ] list packages installed
# - [ ] search packages
# - [ ] in search show what pkgs are out of date

version = 0.1

require "colorize"
require "levenshtein"
require "json"

# colors
Colorize.enabled = Colorize.on_tty_only!()

# load files, first we check if they exist
unless File.exists?("/etc/nemesis-pkg/config.json") && File.exists?("/etc/nemesis-pkg/pkgdata.json") 
    puts "=> #{"error:".colorize(:red)} neccesary files not found."
    Process.exit(1)
end

# arguement parser
begin
    if ARGV[0] == "version" || ARGV[0] == "v"
        puts "=> npkg-query #{version}"
        puts "=> built by Crystal #{Crystal::VERSION} for #{Crystal::HOST_TRIPLE}"
    end
rescue
    puts "=> #{"error:".colorize(:red)} some error occured."
    Process.exit(1)
end