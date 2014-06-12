##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)
##  Use, modification and distribution are subject to the Boost Software License, Version 1.0.
##  (See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt).

import sys

def get():
    return (context_data, golden, source, 'django', ('', {}, False, [], {}, [library_loader], []))

class Library(object):
    def __init__(self, tags={}, filters={}):
        self.tags = tags
        self.filters = filters

def dump(n, x): print n, '=', x; return x

def render_block(segments, context_data, index=0):
    # print '### render_block(', segments, ')'
    renderer = segments[index][1]
    return renderer(context_data)

def dummy_tag():
    return ((lambda segments: ''), None, None)

def monadic_tag(fn, plain=False):
    return variadic_tag(fn, None, None, None, plain=plain)

def dyadic_tag(fn, first, last, plain=False):
    return variadic_tag(fn, first, None, (last,), plain=plain)

def triadic_tag(fn, first, middle, last, plain=False):
    return variadic_tag(fn, first, (middle,), (last,), plain=plain)

def variadic_tag(fn, first, middles, lasts, plain=False):
    if plain:
        return (lambda segments:
                    (lambda context_data, *args, **kwargs:
                        str(fn(*args, **kwargs))), middles, lasts)
    else:
        return (lambda segments:
                    (lambda context_data, *args, **kwargs:
                        str(fn(context_data, segments, *args, **kwargs))), middles, lasts)



def dummy_filter():
    return None

def value_filter(fn):
    return fn


def library_loader(name):
    if name == 'empty_library':
        return Library()

    elif name == 'dummy.tags.and.filters':
        return Library(
            tags={'a': dummy_tag(), 'b': dummy_tag(), 'c': dummy_tag()},
            filters={'x': dummy_filter(), 'y': dummy_filter(), 'z': dummy_filter()},
        )

    elif name == 'test_tags':
        return Library(tags={
            # Monadic ('simple') tags:
            'answer_to_life': monadic_tag(answer_to_life, plain=True), # Nullary
            'identity':       monadic_tag(identity,       plain=True), # Unary
            'ackermann':      monadic_tag(ackermann,      plain=True), # Binary
            'add':            monadic_tag(add,            plain=True), # N-ary
            'set':            monadic_tag(set_variable),
            'unset':          monadic_tag(unset_variable),
            # Polyadic ('block') tags:
            'encode':         dyadic_tag(encode, 'encode', 'endencode'),
            'decode':         dyadic_tag(decode, 'decode', 'enddecode'),
            'unless':         triadic_tag(unless, 'unless', 'otherwise', 'endunless'),
            'f':              variadic_tag(fml, 'f', ('m1', 'm2'), ('l1', 'l2', 'l3',)),
        })

    elif name == 'test_filters':
        return Library(filters={'flip': value_filter(flip)})

    else:
        raise Exception('Library not found')

def flip(s):
    return ''.join(map(lambda c: c.upper() if c.islower() else c.lower(), s))

def answer_to_life():
    return 42

def identity(x):
    return x

def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))

def add(*args):
    return sum(args)

def encode(context_data, segments, arg):
    # print '### encode(', arg, ')'
    s = render_block(segments, context_data)
    return s.encode(arg)

def decode(context_data, segments, arg):
    # print '### decode(', arg, ')'
    s = render_block(segments, context_data)
    return s.decode(arg)

def unless(context_data, segments, arg):
    # print '### unless(', repr(segments), repr(arg), ')'
    pieces, renderer = segments[1 if arg else 0]
    return renderer(context_data)

def set_variable(context_data, segments, *args, **kwargs):
    # print '### set(', args, kwargs, ')'
    pieces = segments[0][0]
    name  = pieces[2]
    value = pieces[3]
    context_data[name] = value
    return ''

def unset_variable(context_data, segments, *args, **kwargs):
    # print '### unset(', args, kwargs, ')'
    pieces = segments[0][0]
    name = pieces[2]
    del context_data[name]
    return ''

def fml(context_data, segments, *args, **kwargs):
    return str(len(segments) - 1)



context_data = {'motto': 'May the Force be with you.'}
source = """\
{% load empty_library %}
{% load a x b y c z from dummy.tags.and.filters %}
{% load flip from test_filters %}
{{ motto }}
{{ motto|flip }}
{% load ackermann from test_tags %}
{% load identity from test_tags %}
{% load answer_to_life from test_tags %}
{% load add from test_tags %}
{% load set unset from test_tags %}
{% load encode decode from test_tags %}
{% load unless from test_tags %}
{% load f from test_tags %}
({% answer_to_life %})
({% identity 'wow' %})
({% ackermann 3 4 %})
({% add %})
({% add 1.1 %})
({% add 1.1 2.2 %})
({% add 1.1 2.2 3.3 %})
{% set foo bar %}({{ foo }})
{% unset foo bar %}({{ foo }})
({% encode 'rot13' %}Hello Kitty{% endencode %})
({% encode 'rot13' %}{{ 'foo'|upper }}{% endencode %})
({% decode 'rot13' %}|{% encode 'rot13' %}Hello Kitty{% endencode %}|{% enddecode %})
({% encode 'rot13' %}|{% encode 'rot13' %}Hello Kitty{% endencode %}|{% endencode %})
({% encode 'rot13' %}{% if True %}Hello Kitty{% endif %}{% endencode %})
({% encode 'rot13' %}{% if False %}Hello Kitty{% endif %}{% endencode %})
({% if True %}{% encode 'rot13' %}Hello Kitty{% endencode %}{% endif %})
({% if False %}{% encode 'rot13' %}Hello Kitty{% endencode %}{% endif %})
({% unless True%}A{% otherwise %}B{% endunless %})
({% unless False%}A{% otherwise %}B{% endunless %})
({% f %}1{% l1 %})
({% f %}1{% l2 %})
({% f %}1{% l3 %})
({% f %}2{% m1 %}2{% l1 %})
({% f %}2{% m1 %}2{% l2 %})
({% f %}2{% m1 %}2{% l3 %})
({% f %}2{% m2 %}2{% l1 %})
({% f %}2{% m2 %}2{% l2 %})
({% f %}2{% m2 %}2{% l3 %})
({% f %}3{% m1 %}3{% m1 %}3{% l1 %})
({% f %}3{% m1 %}3{% m1 %}3{% l2 %})
({% f %}3{% m1 %}3{% m1 %}3{% l3 %})
({% f %}3{% m1 %}3{% m2 %}3{% l1 %})
({% f %}3{% m1 %}3{% m2 %}3{% l2 %})
({% f %}3{% m1 %}3{% m2 %}3{% l3 %})
({% f %}3{% m2 %}3{% m1 %}3{% l1 %})
({% f %}3{% m2 %}3{% m1 %}3{% l2 %})
({% f %}3{% m2 %}3{% m1 %}3{% l3 %})
({% f %}3{% m2 %}3{% m2 %}3{% l1 %})
({% f %}3{% m2 %}3{% m2 %}3{% l2 %})
({% f %}3{% m2 %}3{% m2 %}3{% l3 %})
({% f %}4{% m1 %}4{% m1 %}4{% m1 %}4{% l1 %})
"""
golden = """\



May the Force be with you.
mAY THE fORCE BE WITH YOU.








(42)
(wow)
(125)
(0)
(1.1)
(3.3)
(6.6)
(bar)
()
(Uryyb Xvggl)
(SBB)
(|Hello Kitty|)
(|Hello Kitty|)
(Uryyb Xvggl)
()
(Uryyb Xvggl)
()
(B)
(A)
(1)
(1)
(1)
(2)
(2)
(2)
(2)
(2)
(2)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(3)
(4)
"""

