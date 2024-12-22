# npkg-query: package searcher for nemesis-pkg

version = 0.1

require "colorize"
require "levenshtein"
require "json"

# colors
Colorize.enabled = Colorize.on_tty_only!()

# load files, first we check if they exist
unless File.exists?("/etc/nemesis-pkg/config.json") && File.exists?("/etc/nemesis-pkg/pkgdata.json") 
    puts "=> #{"error:".colorize(:red)} neccesary files not found."
end
 