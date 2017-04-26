{
  "apiVersion": "apps/v1beta1",
  "kind": "StatefulSet",
  "metadata": {
    "name": "{{ name }}",
    "namespace": "{{ namespace }}"
  },
  "spec": {
    "serviceName": "node",
    "replicas": {{ replicas }},
    "template": {
      "metadata": {
        "labels": {
          "owner": "{{ owner }}",
          "app": "ambari",
          "cluster": "{{ cluster }}",
          "role": "server"
        }
      },
      "spec": {
        "terminationGracePeriodSeconds": 10,
        "containers": [
          {
            "name": "{{ name }}",
            "image": "kpaasv2/ambari-server:1.0.0",
            "resources": {
              "limits": {
                "cpu": 4,
                "memory": "8Gi"
              },
              "requests": {
                "cpu": 4,
                "memory": "8Gi"
              }
            },
            "ports": [
              {
                "containerPort": 8080,
                "name": "ui"
              },
              {
                "containerPort": 8440,
                "name": "tran"
              },
              {
                "containerPort": 8441,
                "name": "tran2"
              }
            ],
            "securityContext": {
              "privileged": true
            }
          }
        ]
      }
    }
  }
}