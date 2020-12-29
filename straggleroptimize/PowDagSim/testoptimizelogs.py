import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-op', '--optimize23',default="1")
args = parser.parse_args()
print(args.optimize23)