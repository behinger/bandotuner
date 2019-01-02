# This script starts the bokeh server
import streamer_v2 # so that pyinstaller finds it
from bokeh.command.subcommands.serve import Serve
import argparse

    
p = argparse.ArgumentParser()
s = Serve(p)
# Set up your command line arguments here by directly modifying args.
args = p.parse_args(args='')
args.show = True
args.files.append('streamer_v2.py')
s.invoke(args)