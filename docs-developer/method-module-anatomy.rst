

An analysis module lik PCA is an plugin.

The setup is partially base on the Dataflow programming (http://en.wikipedia.org/wiki/Dataflow_programming) paradigm.

Each plugin (modul) is an statistical method.

The method takes on or several input data and have a set of settings.

When the calculation is made, it returns a result.

The calculation settings is a part of the method object and is statefull.

The method imput data is not part of the calculation method. But via the GUI assosicate a single input or a related input set to the method.

That association represent an defined calculation that can yield several different result sets depending on the method settings.

The GUI for the method is divided in two parts. One part is a tree that shows all the defined calculations.
The sub branches represent various results and ways to present it.

The other part of the GUI is an 'control panel' that is also divided into two parts. One part is the warious settings for the method. The other part let the user decide the wanted configuration for the input data.


Structure

Vi have av PCA plugin object.
This plugin object have av PCA model object with the model calculation and model settings.
The plugin have a list of datasets avaiable for PCA.
The plugin have a list of datasets that is selected for PCA.




Events

