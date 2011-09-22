Coding standard for ConsumerCheck
*********************************

Inspiration and guideline

http://www.python.org/dev/peps/pep-0008/

Indentation preferably with tab but as long as Spyder do not support tab do we have to use 4 space.

Classnames: CamelCase
Method names: camelCase()
Variables names: camelCase

Module name: short lowercase

      Function names should be lowercase, with words separated by underscores
      as necessary to improve readability.

      mixedCase is allowed only in contexts where that's already the
      prevailing style (e.g. threading.py), to retain backwards compatibility.

      Use the function naming rules: lowercase with words separated by
      underscores as necessary to improve readability.


Things to fix

ds._ds_id -> ds._id
_changed -> on_trait_change
file_importer: separate conf file handling as separate module
file_importer: plugin module for text file reader and xls reader
file_importer: settings for comma and dot, utf-8 and other encodings, tab or comma separated
