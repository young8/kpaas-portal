{
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "labels": {
            "name": "{{ name }}"
        },
        "name": "{{ name }}"
    },
    "spec": {
        "ports": [
            {
                "protocol": "TCP",
                "port": 8080,
                "targetPort": 8080
            }
        ],
        "selector": {
            "name": "{{ pod }}"
        },
        "type": "LoadBalancer"
    }
}