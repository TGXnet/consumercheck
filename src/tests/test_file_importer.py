
import unittest
import test_tools

# ConsumerCheck imports
from file_importer import FileImporter


class TestReadDataFile(unittest.TestCase):

    def setUp(self):
        self.testDir = test_tools.findApplicationBasePath() + '/datasets/'
        self.tested = FileImporter()

    def tearDown(self):
        pass

    ## def test1Text1Import(self):
    ##     ds_fn = self.testDir + 'Ost_sensorikk.txt'
    ##     ds = self.tested.import_noninteractive(ds_fn)
    ##     self.assertEqual(ds.nCols, 20)
    ##     self.assertEqual(ds.nRows, 7)

    ## def test2Text2Import(self):
    ##     ds_fn = self.testDir + 'Ost_forbruker.txt'
    ##     ds = self.tested.import_noninteractive(ds_fn)
    ##     self.assertEqual(ds.nCols, 36)
    ##     self.assertEqual(ds.nRows, 7)

    ## def testReadVarnameObjecnameDatafile(self):
    ##      readTest = FileImporter(self.testDir + 'C_lables.txt', True, True)
    ##      readTest.readFile()
    ##      matrix = readTest.getMatrix()
    ##      nRows, nCols = matrix.shape
    ##      self.assertEqual(nRows, 21)
    ##      self.assertEqual(nCols, 3)
    ##      varNames = readTest.getVariableNames()
    ##      nVarName = len(varNames)
    ##      self.assertEqual(nVarName, nCols)
    ##      objNames = readTest.getObjectNames()
    ##      nObjNames = len(objNames)
    ##      self.assertEqual(nObjNames, nRows)

    ## def test3XlsImport(self):
    ##     ds_fn = self.testDir + 'Ost_sensorikk.xls'
    ##     ds = self.tested.import_noninteractive(ds_fn)
    ##     self.assertEqual(ds.nCols, 20)
    ##     self.assertEqual(ds.nRows, 7)

    def test2InteractiveImport(self):
         ds = self.tested.import_interactive()
         ds.print_traits()


if __name__ == '__main__':
    unittest.main()
