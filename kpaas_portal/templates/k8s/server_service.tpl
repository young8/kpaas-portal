{
  "apiVersion": "v1",
  "kind": "Service",
  "metadata": {
    "name": "{{ name }}",
    "namespace": "{{ namespace }}"
  },
  "spec": {
    "ports": [
      {
        "port": 8080,
        "name": "ui"
      },
      {
        "port": 8440,
        "name": "tran"
      },
      {
        "port": 8441,
        "name": "tran2"
      }
    ],
    "selector": {
      "owner": "{{ owner }}",
      "cluster": "{{ cluster }}",
      "app": "ambari",
      "role": "server"
    },
    "type": "NodePort"
  }
}