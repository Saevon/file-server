__complete_file_server()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=
    opts+=" --host --open"
    opts+=" -h --help"
    opts+=" -p --port"
    opts+=" -v --debug --verbose -q --quiet"
    opts+=" -u --upload"
    opts+=" -r --root"

    # Port completion
    if [[ "${prev}" == "-p" || "${prev}" == "--port" ]]; then
        COMPREPLY=( $(compgen -W "{0..65535}" -- ${cur}) )

        return 0
    # Upload Directory
    elif [[ "${prev}" == "-u" || "${prev}" == "--upload" ]]; then
        COMPREPLY=( $(compgen -A directory -- ${cur}) )

        return 0
    #
    elif [[ "${prev}" == "-r" || "${prev}" == "--root" ]]; then
        COMPREPLY=( $(compgen -A file -- ${cur}) )

        return 0
    else
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )

        return 0
    fi
}
complete -F __complete_file_server file_server.py
