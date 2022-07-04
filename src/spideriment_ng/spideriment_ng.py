#!/bin/false

# Copyright (c) 2022 Vít Labuda. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def _set_import_paths() -> None:
    import sys
    import os.path

    program_src_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

    if program_src_dir not in sys.path:
        sys.path.insert(0, program_src_dir)

    for unwanted_path in ("", ".", ".."):
        while unwanted_path in sys.path:  # The path may be in the list more than once
            sys.path.remove(unwanted_path)


def _set_resource_limits() -> None:
    import resource

    # File descriptor limit - set hard limit as soft limit
    fd_hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    resource.setrlimit(resource.RLIMIT_NOFILE, (fd_hard_limit, fd_hard_limit))


def _get_config_file_path() -> str:
    import sys

    try:
        return sys.argv[1]
    except IndexError:
        raise RuntimeError("The first argument passed to this program must be a configuration file path!")


def _main() -> None:
    _set_import_paths()
    _set_resource_limits()
    config_file_path = _get_config_file_path()

    from spideriment_ng.supervisor.SupervisorMain import SupervisorMain
    SupervisorMain().main(config_file_path)


if __name__ == '__main__':
    _main()
