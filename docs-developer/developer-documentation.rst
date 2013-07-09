
=========================
 Developer documentation
=========================

.. toctree::
   :numbered:

   domain-model
   housekeeping
   tools-and-building-blocks
   data-structures
   plugin-arkitektur
   event-driven
   statistical-methods
   plotting


Code metric
===========

deb: pymetrics
Script som sjekke ut versjonshistorien og teller kodelinjer
COCOMO 2's SLOG Metric fra pymetrics

https://github.com/blackducksw/ohcount
https://www.assembla.com/code/tahar/subversion/nodes
http://liangsun.org/posts/python-code-for-counting-loclines-of-code/
http://cloc.sourceforge.net/

find /my/source -name "*.py" -type f -exec cat {} + | wc -l

# find the combined LOC of files
# usage: loc Documents/fourU py html
function loc {
    #find $1 -name $2 -type f -exec cat {} + | wc -l
    namelist=''
    let i=2
    while [ $i -le $# ]; do
        namelist="$namelist -name \"*.$@[$i]\""
        if [ $i != $# ]; then
                namelist="$namelist -or "
        fi
        let i=i+1
    done
    #echo $namelist
    #echo "find $1 $namelist" | sh
    #echo "find $1 $namelist" | sh | xargs cat
    echo "find $1 $namelist" | sh | xargs cat | wc -l
}


loc() { D=$1; shift echo "$@" | xargs -n 1 echo | sed 's,^, -or -name *.,' | xargs find $D -type f | xargs cat | wc -l }


echo py html | xargs -n 1 echo | sed 's,^, -or -name *.,' | xargs find Documents -type f | xargs cat | wc -l
