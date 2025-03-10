# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from llnl.util import tty

from spack.package import *


class Amdlibm(SConsPackage):
    """AMD LibM is a software library containing a collection of basic math
    functions optimized for x86-64 processor-based machines. It provides
    many routines from the list of standard C99 math functions.
    Applications can link into AMD LibM library and invoke math functions
    instead of compiler's math functions for better accuracy and
    performance.

    LICENSING INFORMATION: By downloading, installing and using this software,
    you agree to the terms and conditions of the AMD AOCL-FFTW license
    agreement.  You may obtain a copy of this license agreement from
    https://www.amd.com/en/developer/aocl/libm/eula/libm-4-2-eula.html
    https://www.amd.com/en/developer/aocl/libm/libm-eula.html
    """

    _name = "amdlibm"
    homepage = "https://www.amd.com/en/developer/aocl/libm.html"
    git = "https://github.com/amd/aocl-libm-ose.git"
    url = "https://github.com/amd/aocl-libm-ose/archive/refs/tags/3.0.tar.gz"
    maintainers("amd-toolchain-support")

    license("BSD-3-Clause")

    version(
        "4.2",
        sha256="58847b942e998b3f52eb41ae26403c7392d244fcafa707cbf23165aac24edd9e",
        preferred=True,
    )
    version("4.1", sha256="5bbbbc6bc721d9a775822eab60fbc11eb245e77d9f105b4fcb26a54d01456122")
    version("4.0", sha256="038c1eab544be77598eccda791b26553d3b9e2ee4ab3f5ad85fdd2a77d015a7d")
    version("3.2", sha256="c75b287c38a3ce997066af1f5c8d2b19fc460d5e56678ea81f3ac33eb79ec890")
    version("3.1", sha256="dee487cc2d89c2dc93508be2c67592670ffc1d02776c017e8907317003f48845")
    version("3.0", sha256="eb26b5e174f43ce083928d0d8748a6d6d74853333bba37d50057aac2bef7c7aa")
    version("2.2", commit="4033e022da428125747e118ccd6fdd9cee21c470")

    variant("verbose", default=False, description="Building with verbosity", when="@:4.1")

    # Mandatory dependencies
    depends_on("python@3.6.1:", type=("build", "run"))
    depends_on("scons@3.1.2:", type=("build"))
    depends_on("mpfr", type=("link"))
    for vers in ["4.1", "4.2"]:
        with when(f"@{vers}"):
            depends_on(f"aocl-utils@{vers}")

    patch("0001-libm-ose-Scripts-cleanup-pyc-files.patch", when="@2.2")
    patch("0002-libm-ose-prevent-log-v3.c-from-building.patch", when="@2.2")

    conflicts("%gcc@:9.1.0", msg="Minimum supported GCC version is 9.2.0")
    conflicts("%gcc@13.2.0:", msg="Maximum supported GCC version is 13.1.0")
    conflicts("%clang@9.0:16.0", msg="supported Clang version is from 9 to 16")
    conflicts("%aocc@3.2.0", msg="dependency on python@3.6.2")

    def build_args(self, spec, prefix):
        """Setting build arguments for amdlibm"""
        args = ["--prefix={0}".format(prefix)]

        if self.spec.satisfies("@4.1: "):
            args.append("--aocl_utils_install_path={0}".format(self.spec["aocl-utils"].prefix))

        if not (
            self.spec.satisfies(r"%aocc@3.2:4.2")
            or self.spec.satisfies(r"%gcc@12.2:13.1")
            or self.spec.satisfies(r"%clang@15:16")
        ):
            tty.warn(
                "AOCL has been tested to work with the following compilers\
                    versions - gcc@12.2:13.1, aocc@3.2:4.2, and clang@15:16\
                    see the following aocl userguide for details: \
                    https://www.amd.com/content/dam/amd/en/documents/developer/version-4-2-documents/aocl/aocl-4-2-user-guide.pdf"
            )

        # we are circumventing the use of
        # Spacks compiler wrappers because
        # SCons wipes out all environment variables.
        if self.spec.satisfies("@:3.0 %aocc"):
            args.append("--compiler=aocc")

        var_prefix = "" if self.spec.satisfies("@:3.0") else "ALM_"
        args.append("{0}CC={1}".format(var_prefix, self.compiler.cc))
        args.append("{0}CXX={1}".format(var_prefix, self.compiler.cxx))

        # Always build verbose
        args.append("--verbose=1")

        return args

    install_args = build_args

    @run_after("install")
    def create_symlink(self):
        """Symbolic link for backward compatibility"""
        with working_dir(self.prefix.lib):
            os.symlink("libalm.a", "libamdlibm.a")
            os.symlink("libalm.so", "libamdlibm.so")
            if self.spec.satisfies("@4.0:"):
                os.symlink("libalmfast.a", "libamdlibmfast.a")
                os.symlink("libalmfast.so", "libamdlibmfast.so")
