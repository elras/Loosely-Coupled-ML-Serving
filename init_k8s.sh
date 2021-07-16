kubectl create namespace gpu-resources ml-system
kubectl apply -f nvidia-device-plugin-ds
kubectl apply -f keda-2.3.0.yaml
