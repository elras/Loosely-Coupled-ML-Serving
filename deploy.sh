# Container parameters
KUBECTL_OPERATION=apply # OR delete
CONTAINER_IMAGE= # SET
SERVICE_BUS_CONNECTION_STRING=  # SET

# Auto-scaling parameters
QUEUE_NAME= # SET
MIN_REPLICAS=1
MAX_REPLICAS=8
SCALEUP_MESSAGE_PATIENCE=8

# Deployment
cat << EOF | kubectl ${KUBECTL_OPERATION} -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: classifier
  namespace: ml-system
  labels:
    app: classifier
spec:
  selector:
    matchLabels:
      app: classifier
  template:
    metadata:
      labels:
        app: classifier
    spec:
      containers:
      - name: worker-0
        image: ${CONTAINER_IMAGE}
        imagePullPolicy: IfNotPresent
        env:
        - name: SERVICE_BUS_CONNECTION_STRING # Used by both Keda and worker
          value: ${SERVICE_BUS_CONNECTION_STRING}
        resources:
          limits:
            nvidia.com/gpu: 1 # Allows us to scale the k8s cluster machines
      - name: worker-1
        image: ${CONTAINER_IMAGE}
        imagePullPolicy: IfNotPresent
        env:
        - name: SERVICE_BUS_CONNECTION_STRING
          value: ${SERVICE_BUS_CONNECTION_STRING}
        - name: NVIDIA_VISIBLE_DEVICES 
          value: "all" # Allows us to reach the GPU from other containers
---
apiVersion: keda.sh/v1alpha1 
kind: ScaledObject
metadata:
  name: classifier-scaler
  namespace: keda-system
spec:
  scaleTargetRef:
    name: classifier
  minReplicaCount: ${MIN_REPLICAS}
  maxReplicaCount: ${MAX_REPLICAS} # Default: 100
  pollingInterval: 5 # Optional, default 30 seconds
  cooldownPeriod: 300 # Optional, default 300 seconds
  triggers:
  - type: azure-servicebus
    metadata:
      queueName: ${QUEUE_NAME}
      messageCount: '${SCALEUP_MESSAGE_PATIENCE}'
      connectionFromEnv: SERVICE_BUS_CONNECTION_STRING
EOF