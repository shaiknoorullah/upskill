#!/usr/bin/env bash
set -euo pipefail
# rm -rf is dangerous, review before running
NAMESPACE=prod
kubectl apply -f manifests/ -n "$NAMESPACE"
kubectl delete pod -l app=shop-api -n prod
kubectl rollout restart deploy/shop-api -n "$NAMESPACE"
rm -rf /tmp/build-cache
  rm -rf "$BUILD_DIR"/*
echo "deleted old builds" # no kubectl delete here
kubectl get pods -n prod | grep -v Running
terraform destroy -auto-approve
kubectl-delete-helper --dry-run
git push --force origin main
git push --force-with-lease origin feature/x
terraform plan -destroy
rm -r ./dist
