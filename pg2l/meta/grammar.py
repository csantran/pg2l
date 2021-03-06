# -*- coding : utf-8 -*-
#    Copyright (C) 2018 by
#    Cédric Santran <santrancedric@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:
#    Cédric Santran <santrancedric@gmail.com>
import types
from collections import namedtuple, UserList


import networkx as nx

class GrammarItem(UserList):
    def __repr__(self):
        return '(%s %s)' % (type(self).__name__, ','.join(repr(x) for x in self))

    def __str__(self):
        return '%s' % ''.join(str(x) for x in self if x)


class MetaGrammar(nx.DiGraph):
    symbols = None

    @property
    def axiom(self):
        inputs = [n for n in self.nodes() if not
                     [p for p in self.predecessors(n) if p != n]]

        return inputs[0] if len(inputs) == 1 else None

    @property
    def terminals(self):
        return set([n for n in self.nodes() if
                            self.out_degree(n) == 0 and n != 'empty'])

    @property
    def nonterminals(self):
        return self.alphabet - self.terminals

    @property
    def alphabet(self):
        return set(self.nodes())

    @property
    def productions(self):
        productions = {}

        for u,_,data in self.edges(data=True):

            if u not in productions:
                productions[u] = []

            for prod in data['production']:
                prod_hash = ''.join(str(x) for x in prod)

                if prod_hash not in productions[u]:
                    productions[u].append(prod_hash)
                    yield (u, prod)

    def set_symbols(self, symbols):
        self.symbols = symbols

    @staticmethod
    def add_production(graph, declaration):
        lhs, rhs = declaration[0], declaration[1:]

        if lhs not in graph.nodes:
            graph.add_node(lhs)

        if len(rhs) == 1 and isinstance(rhs[0], (list, tuple, types.GeneratorType, range)):
            for symbol in rhs[0]:
                if graph.has_edge(lhs, symbol):
                    raise Exception()
                else:
                    graph.add_edge(lhs, symbol, production=[[symbol]])
        else:

            for symbol in rhs:
                if graph.has_edge(lhs, symbol):
                    graph[lhs][symbol]['production'].append(rhs)
                else:
                    graph.add_edge(lhs, symbol, production=[rhs])

    @staticmethod
    def from_declaration(*declarations):
        G = MetaGrammar()

        for declaration in declarations:
            MetaGrammar.add_production(G, declaration)

        Symbol = namedtuple('Symbol', G.nonterminals)
        symbols = Symbol(**{name:type(name, (GrammarItem,), {}) for name in G.nonterminals})
        G.set_symbols(symbols)
        return G

    @staticmethod
    def from_string(string):
        raise NotImplementedError()

    def __add__(self, grammar):
        if not isinstance(grammar, MetaGrammar):
            raise Exception()

        return MetaGrammar(nx.compose(self, grammar))
