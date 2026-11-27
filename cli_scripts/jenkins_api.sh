#!/bin/bash

jenkins_api_run() {
    local pod
    if [ -n "${_CLI_RUNNER_DEBUG:-}" ]; then
        printf 'Jenkins REST command:' >&2
        printf ' %q' "$@"
        printf '\n' >&2
    fi

    if command -v kubectl >/dev/null 2>&1; then
        pod=$(kubectl get pods -n nita -l io.kompose.service=jenkins \
            -o jsonpath='{.items[0].metadata.name}') || return
        if [ -z "$pod" ]; then
            echo "Error: no Jenkins pod found in namespace nita." >&2
            return 1
        fi
        kubectl exec -i "$pod" -n nita -- \
            python3 /usr/local/bin/jenkins_api.py "$@"
    elif command -v docker >/dev/null 2>&1; then
        docker exec -i nitajenkins_jenkins_1 \
            python3 /usr/local/bin/jenkins_api.py "$@"
    else
        echo "Error: cannot find required kubectl or docker binary." >&2
        return 1
    fi
}
