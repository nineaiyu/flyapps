#!/bin/bash
function cleanup()
{
    local pids=`jobs -p`
    if [[ "${pids}" != ""  ]]; then
        kill ${pids} >/dev/null 2>/dev/null
    fi
}

action="${1-start}"
service="${2-all}"

trap cleanup EXIT

rm -f tmp/*.pid

if [[ "$action" == "bash" || "$action" == "sh" ]];then
    bash
else
    python manage.py "${action}" "${service}" -u nginx -usm  1
fi

