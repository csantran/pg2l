# -*- coding : utf-8 -*-
#    Copyright (C) 2018 by
#    Cédric Santran <santrancedric@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:
#    Cédric Santran <santrancedric@gmail.com>
"""
pG2L abstract syntax tree
"""
from .base import Leaf
from .base import BTree as Infix
from .base import BTreeLeft as LeftOperand
from .base import BTreeRight as RightOperand
from .base import KTree as Container
from .base import BaseTree

"""
*********
Terminals
*********

Terminals ast classes 
"""

class Terminal(Leaf):
    """
    A simple terminal object that contains data

    Parameters
    ----------
    data : dict
        terminal data's
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs

class Symbol(Terminal, LeftOperand):
    """A symbol, a letter and some parameters"""
    repr_string = '(Symbol %s)'

    def __str__(self):
        return self.data['symbol']

class Empty(Symbol):
    """The empty symbol"""
    repr_string = '(ε%s)'
    def __init__(self, **kwargs):
        super().__init__(symbol='')

class Jump(Terminal, LeftOperand):
    """A Jump, a number and some parameters"""
    repr_string = '(Jump %s)'

    def __str__(self):
        return str(self.data['jump'])

"""
************
Nonterminals
************

Nonterminals ast classes

*****
Atoms
*****
"""

class ATOM(Infix):
    """Atom, base classe for :obj:`NODE` and a :obj:`MODULE`, basic element of a string"""
    pass

class NODE(ATOM):
    """Node base class"""
    pass

class MODULE(ATOM):
    """Module base class"""
    def __str__(self):
        """String representation of a module"""
        return '[%s]' % super().__str__()

class SYM(ATOM):
    """An atom with only a symbol on his left side"""
    repr_string = '(SYM %s)'

class CSYM(Symbol):
    """An atom with a symbol on the left and a round of jumps on his right side"""
    repr_string = '(CSYM %s)'

class MOD(MODULE):
    """An Atom with only a level on his left side"""
    repr_string = '(MOD %s)'

class CMOD(MODULE):
    """An atom with a level on the left and a round of jump on the right side"""
    repr_string = '(CMOD %s)'

    def __str__(self):
        """String representation of a connected module"""
        return '[%s]%s' % (self.left, self.right)

class LEVEL(Container, LeftOperand):
    """A level, 
    container for atoms, that is, it contains the nodes and modules of the same level"""
    repr_string = '(LEVEL %s)'

class Round(Container, RightOperand):
    """A round, 
    container for jumps"""
    repr_string = '(Round %s)'

"""
******
String
******
"""

class String(Container):
    """A string, a word of the language, a set of atoms
    """
    rep_string = '(STRING %s)'
    
"""
****************
Production rules
****************
"""

class Predecessor(String, LeftOperand):
    """Predecessor,
    left part of a rewriting rule"""
    pass

class Successor(String, RightOperand):
    """Predecessor,
    right part of a rewriting rule"""
    pass

class Rule(Infix, LeftOperand):
    """Rule, 
    the rewriting rule composed of the predecessor on the left 
    and the successor on the right
    """
    @property
    def predecessor(self):
        """predecessor getter"""
        return self.left

    @property
    def successor(self):
        """successor getter"""
        return self.right

"""
*******
Context
*******
"""

class Contexts(Container, RightOperand):
    """Context of a production rule,
    contains context strings"""
    pass

class ContextString(String):
    """Context string base classe"""
    pass

class GraphLeftContext(ContextString):
    """Left-context seen from the point of view of the graph representation"""
    pass

class GraphRightContext(ContextString):
    """Right-context seen from the point of view of the graph representation"""
    pass

class StringLeftContext(ContextString):
    """Left-context seen from the point of view of the string representation"""
    pass

class StringRightContext(ContextString):
    """Right-context seen from the point of view of the string representation"""
    pass

class PRODUCTION(Infix):
    """Production rule base class,
    contains a rewriting rule on his left side
    """
    @property
    def rule(self):
        """rule getter"""
        return self.left

class Identity(PRODUCTION):
    """Identity production where the successor is identical to the predecessor"""
    def __init__(self, predecessor):
        raise NotImplementedError()

class G0L(PRODUCTION):
    """G0L,
    a context-free production rule"""
    repr_string = '(CFP %s)'

    def __str__(self):
        """String representation of a context-free production"""
        return '%s:%s' % (str(self.children[0]), str(self.children[1]))

class G1LL(PRODUCTION):
    """G1LL,
    a non context-free production rule with left-context"""
    repr_string = '(G1LL %s)'

    @property
    def left(self):
        """left context getter"""
        return self.children[2]

    def __str__(self):
        """String representation of a G1LL production"""
        return '%s<%s:%s' % (str(self.children[2]), str(self.children[0]), str(self.children[1]))

    pass

class G1LR(PRODUCTION):
    """G1LR
    a non context-free production rule with right-context"""
    repr_string = '(G1LR %s)'

    @property
    def right(self):
        """right context getter"""
        return self.children[2]

    def __str__(self):
        """String representation of a G1LR production"""
        return '%s>%s:%s' % (str(self.children[0]), str(self.children[2]), str(self.children[1]))

class G2L(PRODUCTION):
    """G2L,
    a non context-free production rule with both left and right context"""
    repr_string = '(G2L %s)'

    @property
    def left(self):
        """left context getter"""
        return self.children[2]

    @property
    def right(self):
        """right context getter"""
        return self.children[3]

    def __str__(self):
        """String representation of a G2LR production"""
        return '%s<%s>%s:%s' % (str(self.children[2]),
                                str(self.children[0]),
                                str(self.children[3]),
                                str(self.children[1]))

# class REWRITE(Leaf):
#     """operator TO"""
#     pass

# class LEFT(Leaf):
#     """operator left context"""
#     pass

# class RIGHT(Leaf):
#     """operator right context"""
#     pass

def copy(obj):
    """Do a shallow copy of tree

    Examples
    --------
    >>> x = Symbol(symbol='B')
    >>> y = copy(x)
    >>> print(y.data)
    {'symbol': 'B'}

    Parameters
    ----------
    tree: :obj:`tree`
       a tree

    Returns
    -------
    :obj:`tree`
        orphaned shallow copy of a tree
    """
    t_copy = isinstance(obj, Terminal) and type(obj)(**dict(obj.data)) or type(obj)()

    if isinstance(obj, BaseTree):
        for child in obj.children:
            t_copy.push(copy(child))

    return t_copy