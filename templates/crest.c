#include <crest.h>

int main(int argc, char** argv) {
    {%
        for {<type>}, {<var>}, {<size>} in {<vp>}:
            if {<type>} == {<"char*">}:
                {<size>} = {<size>} + {<1d>}
                char {<var>}[{<size>}];
            else:
                {<type>} {<var>};

        for {<type>}, {<var>}, {<size>} in {<vp>}:
            if {<type>} == {<"unsigned char">}:
                CREST_unsigned_char({<var>});
            else if {<type>} == {<"unsigned short">}:
                CREST_unsigned_short({<var>});
            else if {<type>} == {<"unsigned int">}:
                CREST_unsigned_int({<var>});
            else if {<type>} == {<"char">}:
                CREST_char({<var>});
            else if {<type>} == {<"short">}:
                CREST_short({<var>});
            else if {<type>} == {<"int">}:
                CREST_int({<var>});
            else :
                ;

        return logic_bomb({<params>});
    %}
}
