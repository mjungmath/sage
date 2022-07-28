r"""
Submodules and subquotients of free modules

Free modules and submodules of a free module (of finite rank) over a principal
ideal domain have well-defined notion of rank, and they are implemented in
:mod:`sage.modules.free_module`. Here submodules with no rank are
implemented. For example, submodules of free modules over multivariate
polynomial rings with more than one variables have no notion of rank.

EXAMPLES::

    sage: S.<x,y,z> = PolynomialRing(QQ)
    sage: M = S**2
    sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
    sage: N
    Submodule of Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z over Rational Field
    Generated by the rows of the matrix:
    [x - y     z]
    [  y*z   x*z]

AUTHORS:

- Kwankyu Lee (2022-05): initial version

"""

# ****************************************************************************
#       Copyright (C) 2022 Kwankyu Lee <ekwankyu@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.modules.free_module import (basis_seq,
                                      Module_free_ambient,
                                      FreeModule_ambient_domain)
from .quotient_module import QuotientModule_free_ambient


class Submodule_free_ambient(Module_free_ambient):
    """
    Base class of submodules of ambient modules.

    The ambient module is either a free module or a quotient of a free module
    by a submodule.

    Note that if the ambient module is a quotient module, submodules
    of the quotient module are called subquotients.

    INPUT:

    - ``ambient`` -- an ambient module

    - ``gens`` -- vectors of the ambient free module generating this submodule

    - ``check`` -- boolean; if ``True``, vectors in ``gens`` are checked whether
      they belong to the ambient free module

    - ``already_echelonized`` -- ignored; for compatibility with other submodules

    EXAMPLES::

        sage: S.<x,y,z> = PolynomialRing(QQ)
        sage: M = S**2
        sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
        sage: N
        Submodule of Ambient free module of rank 2 over the integral domain
        Multivariate Polynomial Ring in x, y, z over Rational Field
        Generated by the rows of the matrix:
        [x - y     z]
        [  y*z   x*z]

    ::

        sage: M.coerce_map_from(N)
        Coercion map:
          From: Submodule of Ambient free module of rank 2 over the integral domain
        Multivariate Polynomial Ring in x, y, z over Rational Field
        Generated by the rows of the matrix:
        [x - y     z]
        [  y*z   x*z]
          To:   Ambient free module of rank 2 over the integral domain
        Multivariate Polynomial Ring in x, y, z over Rational Field
    """
    def __init__(self, ambient, gens, check=True, already_echelonized=False):
        r"""
        Initialize.

        TESTS::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
            sage: N.is_submodule(M)
            True
        """
        if not isinstance(ambient, (FreeModule_ambient_domain, QuotientModule_free_ambient)):
            raise TypeError("ambient (=%s) must be ambient or a quotient" % ambient)
        R = ambient.base_ring()
        degree = ambient.degree()
        sparse = ambient.is_sparse()
        self._ambient = ambient

        if check:
            try:
                # convert generator vectors to elements of the ambient module
                gens = [ambient(x) for x in gens]
            except TypeError:
                raise TypeError("each element of basis must be in the ambient free module")

        Module_free_ambient.__init__(self, base_ring=R, degree=degree, sparse=sparse)

        C = self.element_class
        w = [C(self, x.list(), coerce=False, copy=False) for x in gens if x]
        self.__gens = basis_seq(self, w)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y*z, x*z])])
            sage: N
            Submodule of Ambient free module of rank 2 over the integral domain
            Multivariate Polynomial Ring in x, y, z over Rational Field
            Generated by the rows of the matrix:
            [x - y     z]
            [  y*z   x*z]

            sage: Q = M.quotient_module(N)
            sage: NQ = Q.submodule([Q([1,x])])
            sage: NQ
            Subquotient of Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z over Rational Field
            Generated by the rows of the matrix:
            [1 x]
            With relations matrix:
            [x - y     z]
            [  y*z   x*z]
        """
        if isinstance(self._ambient, QuotientModule_free_ambient):
            return ("Subquotient of %s\n" % self.ambient_module().free_cover() +
                    "Generated by the rows of the matrix:\n%s\n" % self.matrix() +
                    "With relations matrix:\n%s" % self._ambient.free_relations().matrix())
        return ("Submodule of %s\n" % self.ambient_module() +
                "Generated by the rows of the matrix:\n%s" % self.matrix())

    def matrix(self):
        """
        Return the matrix defining ``self``.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y*z, x*z])])
            sage: N.matrix()
            [x - y     z]
            [  y*z   x*z]
        """
        from sage.matrix.matrix_space import MatrixSpace
        MAT = MatrixSpace(self.base_ring(), len(self.gens()), self.degree(),
                          sparse = self.is_sparse())
        A = MAT(self.gens())
        A.set_immutable()
        return A

    generators_matrix = matrix

    def relations(self):
        r"""
        Return the relations module of the ambient module.

        If the ambient module is free, then the relations module is trivial.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
            sage: N.relations() == M.zero_submodule()
            True

            sage: Q = M.quotient(N)
            sage: Q.zero_submodule().relations() == N
            True
        """
        return self._ambient.relations()

    def gens(self):
        """
        Return the generators of this submodule.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
            sage: N.gens()
            [
            (x - y, z),
            (y*z, x*z)
            ]
        """
        return self.__gens

    def gen(self, i=0):
        """
        Return the `i`-th generator of this module.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y*z, x*z])])
            sage: N.gen(0)
            (x - y, z)
        """
        if i < 0 or i >= len(self.__gens):
            raise ValueError('no generator with index %s' % i)
        return self.__gens[i]

    def ambient_module(self):
        """
        Return the ambient module of ``self``.

        EXAMPLES::

            sage: S.<x,y,z> = PolynomialRing(QQ)
            sage: M = S**2
            sage: N = M.submodule([vector([x - y, z]), vector([y * z, x * z])])
            sage: N.ambient_module() is M
            True
            sage: N.zero_submodule().ambient_module() is M
            True
            sage: Q = M / N
            sage: Q.zero_submodule().ambient_module() is Q
            True
        """
        return self._ambient
