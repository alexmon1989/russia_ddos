from sys import version_info as vi, version

if vi.major < 3 or (vi.major == 3 and vi.minor < 9):
  print('Minimum required Python version to run this script is 3.9!')
  print(f'Current version: {version}')
  exit(1)
