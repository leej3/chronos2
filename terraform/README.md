# Resource Deployment

## General Notes

Deployment of infrastructure resources requires [OpenTofu](https://opentofu.org/) (version >=1.8.0).

When calling modules, the relevant input variables can be found in their `variables.tf` file or sometimes their `variables_state.tf` file. This is where the parametrization takes place. In general, a module's `main.tf` file should only be modified if you would like to change what infrastructure is created. Modifying a module's `main.tf` file should seldom be necessary. 

## Repository Secrets and Variables

You must set the following [repository secrets](https://github.com/leej3/chronos2/settings/secrets/actions) before running the GitHub workflows: 

* `AWS_ACCOUNT_ID`: The [AWS account ID](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-identifiers.html#FindAccountId) used for the deployments
* `AWS_REGION`: The AWS region where the deployments reside
* `SSH_PRIVATE_KEY`: The private SSH key used to ssh into the ec2 instances
* `SSH_PUBLIC_KEY`: The public SSH key used to ssh into the ec2 instances
  corresponding to the above private key (use `ssh-keygen -y -f
  path/to/private/key > path/to/public/key` if you have lost the public key, and
  `ssh-keygen -f key.pub -i -m PKCS8` to convert from RSA format)
* `SSH_PROD_HOST`: The static IP address of the production ec2 instance
* `SSH_STAGE_HOST`: The static IP address of the staging ec2 instance
* `LETSENCRYPT_ADMIN_EMAIL`: The email address associated with the Let's Encrypt certificate
* `DEPLOYMENT_USERNAME`: The username used to ssh into the ec2 instances. Defaults to `ubuntu`.
You must also set the following [repository variables](https://github.com/leej3/chronos2/settings/variables/actions) before running the GitHub workflows:

* `PRODUCTION_DEPLOYMENT_URI`: The URL of the production deployment. Probably `'chronos2.org'` (including single quotes `'`)
* `STAGING_DEPLOYMENT_URI`: The URL of the staging deployment. Probably `'dev.chronos2.org'` (including single quotes `'`)
* `TF_VAR_additional_public_key`: The public key of the additional user that has access to the ec2 instance.

## Manual Deployment Steps

### 0. Bootstrap Step: Deploy State Resources

> **_Note:_** This step should be run manually on the developer's/infrastructure engineer's local machine. All subsequent steps will be run automatically by a CD workflow.

> **_Note:_** This step should only be run once for the lifetime of the deployment. 

It is recommended that you use the default variable values, as defined in `modules/state/variables.tf`. If you want to change the values from the defaults, you can add your desired values in `state/main.tf`. You will then need to change the corresponding values in the `variables_state.tf` files of the resources (i.e. `shared`, `staging`, and `production`) to match what you set in `state/main.tf`. This can be done in an automated way by running 

```bash
$ cd ~/path-to-repo/terraform/
$ # Change DynamoDB state lock table names
$ find . -name "*.tf" -exec sed -i '' "s/terraform-state-locks/chronos2-state-locks/g" {} +
$ # Change names of S3 buckets that store OpenTofu state
$ find .  -name "*.tf" -exec sed -i '' "s/chronos2-terraform-state-storage/chronos2-state-storage-test/g" {} +
$ # Change AWS region where state resources reside
$ find . -name "*.tf" -exec sed -i '' "s/us-east-1/us-east-1/g" {} +
```

Once you have configured the variables (or preferably will be using the defaults), you can deploy the state management resources with 

```bash
$ cd ~/path-to-repo/terraform/state/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

> **_NOTE:_** In order to prevent accidental destruction, the `state` modules are configured to [prevent destruction](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle#prevent_destroy) ([more info on `prevent_destroy`](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle#prevent-resource-deletion)) using OpenTofu. To destroy state resources, you must do so manually in the AWS Management Console. 

### 1. Deploy Shared Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

> **_Note:_** Until IAM policies are fixed, this step must also be run manually when deploying the infrastructure for the first time. 

You can deploy the shared resources with 

```bash
$ cd ~/path-to-repo/terraform/shared/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

If you modify the shared deployment, you can redeploy it with 

```bash
$ cd ~/path-to-repo/terraform/shared/
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 2. Deploy Staging Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

You can deploy the staging resources with 

```bash
$ cd ~/path-to-repo/terraform/staging/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

If you modify the staging deployment, you can redeploy it with 

```bash
$ cd ~/path-to-repo/terraform/staging/
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 3. Deploy Production Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

You can deploy the production resources with 

```bash
$ cd ~/path-to-repo/terraform/production/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

If you modify the production deployment, you can redeploy it with 

```bash
$ cd ~/path-to-repo/terraform/production/
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

## Development/Deployment Workflow

In general, once everything is configured and resources are up, the only human interaction necessary is during [deployment to production](#deployment-to-production).

During development, for every push where a file in `terraform` or `.github/workflows/deploy-opentofu.yml` is modified, [`deploy-opentofu.yml`](../../../.github/workflows/deploy-opentofu.yml) will be run, and the actions up to the `tofu plan` steps will be run as feedback for the developer. The `tofu apply` steps will _not_ be run. 

### Deployment to Staging

When pull requests are merged to main, up to two main workflows are run: [`deploy-docker.yml`](../../../.github/workflows/deploy-docker.yml) and [`deploy-opentofu.yml`](../../../.github/workflows/deploy-opentofu.yml).

If none of the files in a pull request are included in `terraform` or `.github/workflows/deploy-opentofu.yml`, then only `deploy-docker.yml` will be run and the Docker image on the staging EC2 instance will be pushed and rerun. 

If any of the files in a pull request is included in `terraform` or `.github/workflows/deploy-opentofu.yml`, then both `deploy-docker.yml` and `deploy-opentofu.yml` will be run. In this case, however, `deploy-docker.yml` will see that paths dealing with OpenTofu were modified and terminate early and successfully without doing anything. At the same time, `deploy-opentofu.yml` will run and redeploy both shared and staging resources to the staging EC2 instance. After running all OpenTofu actions successfully, `deploy-opentofu.yml` will run `deploy-docker.yml` as a child workflow via the [`workflow_call`](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#workflow_call) trigger. This way, the potent parts of `deploy-docker.yml`, i.e. the parts that actually build and deploy images, is only run once per merged pull request. 

### Deployment to Production

The way to deploy to production is to [manually dispatch your desired workflow](#manual-deployment-from-github-actions).

Note that running the OpenTofu deployment to production will _not_ redeploy the shared resources.

### Manual Deployment from GitHub Actions

You can manually deploy the [Docker images](https://github.com/leej3/chronos2/actions/workflows/deploy-docker.yml) and [OpenTofu deployment](https://github.com/leej3/chronos2/actions/workflows/deploy-opentofu.yml) by navigating to the appropriate action and clicking the "Run workflow" button to reveal the associated menu. Using that menu, you can dispatch either workflow from an arbitrary branch in the repository to either staging or production.

Note that running the OpenTofu deployment will automatically run the Docker deployment as a child workflow.

## Implementation Notes

The two main workflows are implemented in [`deploy-docker.yml`](../../../.github/workflows/deploy-docker.yml) and [`deploy-opentofu.yml`](../../../.github/workflows/deploy-opentofu.yml). There are other workflows that are called as child workflows to those two, but they are never called directly themselves. 
