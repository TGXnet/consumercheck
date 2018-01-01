import sys

if sys.platform == 'darwin':
    datas = [
        (r'/Users/thomas/miniconda/envs/cc-env/lib/python2.7/lib2to3/Grammar.txt', 'lib2to3'),
        (r'/Users/thomas/miniconda/envs/cc-env/lib/python2.7/lib2to3/PatternGrammar.txt', 'lib2to3')]
elif sys.platform == 'linux2':
    datas = [
        (r'/usr/lib/python2.7/lib2to3/Grammar.txt', 'lib2to3'),
        (r'/usr/lib/python2.7/lib2to3/PatternGrammar.txt', 'lib2to3')]
else:
    datas = [
        (r'C:\Users\thomas\Miniconda2\envs\cc-env\Lib\lib2to3\Grammar.txt', 'lib2to3'),
        (r'C:\Users\thomas\Miniconda2\envs\cc-env\Lib\lib2to3\PatternGrammar.txt', 'lib2to3')]
