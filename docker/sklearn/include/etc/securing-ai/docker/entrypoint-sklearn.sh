#!/bin/bash
# Script adapted from the work https://github.com/jupyter/docker-stacks/blob/56e54a7320c3b002b8b136ba288784d3d2f4a937/base-notebook/start.sh.
# See copyright below.
#
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the Jupyter Development Team nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Created by argbash-init v2.8.1
# ARG_OPTIONAL_SINGLE([conda-env],[],[Conda environment],[base])
# ARG_OPTIONAL_SINGLE([results-ttl],[],[Job results will be kept for this number of seconds],[500])
# ARG_LEFTOVERS([Queues to watch])
# ARG_DEFAULTS_POS()
# ARGBASH_SET_INDENT([  ])
# ARG_HELP([Securing AI Lab Entry Point\n])"
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.9.0 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, see https://argbash.io for more info


die()
{
  local _ret="${2:-1}"
  test "${_PRINT_HELP:-no}" = yes && print_help >&2
  echo "$1" >&2
  exit "${_ret}"
}


begins_with_short_option()
{
  local first_option all_short_options='h'
  first_option="${1:0:1}"
  test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
_arg_leftovers=()
# THE DEFAULTS INITIALIZATION - OPTIONALS
_arg_conda_env="base"
_arg_results_ttl="500"


print_help()
{
  printf '%s\n' "Securing AI Lab Entry Point
"
  printf 'Usage: %s [--conda-env <arg>] [--results-ttl <arg>] [-h|--help] ... \n' "$0"
  printf '\t%s\n' "... : Queues to watch"
  printf '\t%s\n' "--conda-env: Conda environment (default: 'base')"
  printf '\t%s\n' "--results-ttl: Job results will be kept for this number of seconds (default: '500')"
  printf '\t%s\n' "-h, --help: Prints help"
}


parse_commandline()
{
  _positionals_count=0
  while test $# -gt 0
  do
    _key="$1"
    case "$_key" in
      --conda-env)
        test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
        _arg_conda_env="$2"
        shift
        ;;
      --conda-env=*)
        _arg_conda_env="${_key##--conda-env=}"
        ;;
      --results-ttl)
        test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
        _arg_results_ttl="$2"
        shift
        ;;
      --results-ttl=*)
        _arg_results_ttl="${_key##--results-ttl=}"
        ;;
      -h|--help)
        print_help
        exit 0
        ;;
      -h*)
        print_help
        exit 0
        ;;
      *)
        _last_positional="$1"
        _positionals+=("$_last_positional")
        _positionals_count=$((_positionals_count + 1))
        ;;
    esac
    shift
  done
}


assign_positional_args()
{
  local _positional_name _shift_for=$1
  _positional_names=""
  _our_args=$((${#_positionals[@]} - 0))
  for ((ii = 0; ii < _our_args; ii++))
  do
    _positional_names="$_positional_names _arg_leftovers[$((ii + 0))]"
  done

  shift "$_shift_for"
  for _positional_name in ${_positional_names}
  do
    test $# -gt 0 || break
    eval "$_positional_name=\${1}" || die "Error during argument parsing, possibly an Argbash bug." 1
    shift
  done
}

parse_commandline "$@"
assign_positional_args 1 "${_positionals[@]}"

# OTHER STUFF GENERATED BY Argbash

### END OF CODE GENERATED BY Argbash (sortof) ### ])
# [ <-- needed because of Argbash

shopt -s extglob
set -euo pipefail

###########################################################################################
# Global parameters
###########################################################################################

readonly ai_workdir="${AI_WORKDIR}"
readonly conda_dir="${CONDA_DIR}"
readonly conda_env="${_arg_conda_env}"
readonly job_queues="${_arg_leftovers[*]}"
readonly logname="Container Entry Point"
readonly rq_redis_uri="${RQ_REDIS_URI-}"
readonly rq_results_ttl="${_arg_results_ttl}"

###########################################################################################
# Restrict network access
#
# Globals:
#   None
# Arguments:
#   None
# Returns:
#   None
###########################################################################################

restrict_network_access() {
  if [[ -f /usr/local/bin/install-python-modules.sh ]]; then
    /usr/local/bin/restrict-network-access.sh
  else
    echo "${logname}: ERROR - /usr/local/bin/restrict-network-access.sh script missing"
    exit 1
  fi
}

###########################################################################################
# Secure the container at runtime
#
# Globals:
#   None
# Arguments:
#   None
# Returns:
#   None
###########################################################################################

secure_container() {
  if [[ -f /usr/local/bin/secure-container.sh ]]; then
    /usr/local/bin/secure-container.sh
  else
    echo "${logname}: ERROR - /usr/local/bin/secure-container.sh script missing"
    exit 1
  fi
}

###########################################################################################
# Start Redis Queue Worker
#
# Globals:
#   ai_workdir
#   conda_dir
#   conda_env
#   job_queues
#   lognanme
#   rq_redis_uri
#   rq_results_ttl
# Arguments:
#   None
# Returns:
#   None
###########################################################################################

start_rq() {
  echo "${logname}: starting rq worker"
  echo "${logname}: rq worker --url ${rq_redis_uri} --results-ttl ${rq_results_ttl} \
  ${job_queues}"

  bash -c "\
  source ${conda_dir}/etc/profile.d/conda.sh &&\
  conda activate ${conda_env} &&\
  cd ${ai_workdir} &&\
  rq worker\
  --url ${rq_redis_uri}\
  --results-ttl ${rq_results_ttl}\
  ${job_queues}"
}

###########################################################################################
# Main script
###########################################################################################

secure_container
start_rq
# ] <-- needed because of Argbash