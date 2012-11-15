from traits.api import HasTraits, HTML
from traitsui.api import View, Item

class ConsumerCheckAbout(HasTraits):
    about_html = '''
    <body text="#404040" bgcolor="#f0f0f0">
    <div align="center"><font size="7">About ConsumerCheck</font></div>
    <p align="center">ConsumerCheck is a program for statistical analysis and visualization.</p>
    <p align="center">ConsumerCheck development:<br />Thomas Graff, <a href="http://www.tgxnet.no">TGXnet</a></p>
    <p align="center">Python wrapping of R code and software development management:<br /><a href="http://www.nofima.no/en/person/oliver.tomic">Oliver Tomic</a>, <a href="http://www.nofima.no">Nofima</a></p>
    <p align="center">Version: 0.7.5</p>
    </body>
    '''
    about_render = HTML(about_html)
    traits_view = View(
        Item('about_render',
             show_label=False
             ),
        title="About",
        height=400,
        width=400,
#        resizable=True,
        ok=True,
        )

if __name__ == '__main__':
    ConsumerCheckAbout().configure_traits()
