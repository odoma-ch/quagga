# KGQA Crowdsourcing Database Setup

This guide provides instructions for deploying and managing the KGQA crowdsourcing database using Helm and OpenShift/Kubernetes.

## Prerequisites

- OpenShift CLI (`oc`) installed
- Helm 3 installed
- Access to the OpenShift cluster
- Required environment variables: `$PASSWORD`, `$USERNAME`, `$DATABASE`

## Deployment

### 1. Login to OpenShift

```bash
oc login --web
```

### 2. Deploy MySQL Database

```bash
helm upgrade -i kgqa-crowdsourcing-db oci://registry.paas.psnc.pl/helm/mysql-simple -n graphia-app1-staging \
    --set fullnameOverride=kgqa-crowdsourcing-db --set primary.persistence.size=8Gi \
    --set primary.persistence.storageClass=standard --set auth.password=$PASSWORD \
    --set auth.username=$USERNAME --set auth.database=$DATABASE
```

## Database Access

### Get Administrator Credentials

```bash
echo Username: root
MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace graphia-app1-staging kgqa-crowdsourcing-db -o jsonpath="{.data.mysql-root-password}" | base64 -d)
```

### Connect to Database

#### 1. Run MySQL Client Pod

```bash
kubectl run kgqa-crowdsourcing-db-client --rm --tty -i --restart='Never' --image registry.paas.psnc.pl/base/bitnami/mysql:8.4.4-debian-12-r0 --namespace graphia-app1-staging --env MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --command -- bash
```

#### 2. Copy SQL File to Pod (if needed)

```bash
kubectl cp ./app_database.sql graphia-app1-staging/kgqa-crowdsourcing-db-client:/tmp/app_database.sql
```

#### 3. Connect to Primary Service

Execute within the pod:

```bash
mysql -h kgqa-crowdsourcing-db.graphia-app1-staging.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD" mydb
```

## Database Management

### Clean and Import Database

```bash
mysql -h kgqa-crowdsourcing-db.graphia-app1-staging.svc.cluster.local -uroot -e "DROP DATABASE IF EXISTS \`$DATABASE\`;"
mysql -h kgqa-crowdsourcing-db.graphia-app1-staging.svc.cluster.local -uroot -e "CREATE DATABASE \`$DATABASE\`;"
mysql -h kgqa-crowdsourcing-db.graphia-app1-staging.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD" mydb < app_database.sql
```

## Configuration

- **Namespace**: `graphia-app1-staging`
- **Storage Size**: 8Gi
- **Storage Class**: standard
- **Database Service**: `kgqa-crowdsourcing-db.graphia-app1-staging.svc.cluster.local`

## Docker image update using Helm chart (PSNC architecture)

```
hdsingh@Harshdeeps-MacBook-Air ~/gotriple-pretraining-dataset/data % helm upgrade -i kgqa-crowdsourcing-db oci://registry.paas.psnc.pl/helm/mysql-simple -n graphia-app1-staging \
    --set fullnameOverride=kgqa-crowdsourcing-db \
    --set primary.persistence.size=8Gi \
    --set primary.persistence.storageClass=standard \
    --set auth.password=$PASSWORD \
    --set auth.username=$USERNAME \
    --set auth.database=mydb \
    --set 'image.pullSecrets[0]=registry-paas-psnc' \
    --set image.registry=registry.paas.psnc.pl \
    --set image.repository=graphia/mysql \
    --set image.tag=8.4.4-debian-12-r0-v2 \
    --set image.pullPolicy=Always
```
