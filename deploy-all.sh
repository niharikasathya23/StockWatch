#!/bin/sh
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
sleep 5
kubectl apply -f rest/rest-ingress.yaml
kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f worker/worker-deployment.yaml
cd minio
helm install -f ./minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
sleep 10
cd ..
kubectl apply -f minio/minio-external-service.yaml
# sleep 30
# kubectl apply -f sample-deployment.yaml 
sleep 10
kubectl port-forward --namespace minio-ns svc/minio-proj 9001:9001 &
kubectl port-forward --namespace minio-ns svc/minio-proj 9000:9000 &
kubectl port-forward --namespace default svc/redis 6379:6379 &
kubectl port-forward --namespace default svc/rest-service 5000:5000 & 