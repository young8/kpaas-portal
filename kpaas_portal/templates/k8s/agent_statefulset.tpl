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
          "role": "agent"
        }
      },
      "spec": {
        "terminationGracePeriodSeconds": 10,
        "containers": [
          {
            "name": "{{ name }}",
            "image": "kpaasv2/ambari-agent:1.0.3",
            "resources": {
              "limits": {
                "cpu": 2,
                "memory": "4Gi"
              },
              "requests": {
                "cpu": 2,
                "memory": "4Gi"
              }
            },
            "command": [
              "init",
              "systemd.setenv=AMBARI_SERVER_ADDR={{ ambariserver }}"
            ],
            "ports": [
              {
                "containerPort": 50070,
                "name": "hdfs"
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