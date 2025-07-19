#!/usr/bin/env python3
import subprocess
import sys
import argparse
import os
from dotenv import load_dotenv

def _get_gcloud_project_id():
  """Get the current Google Cloud project ID."""
  try:
    project_id = subprocess.check_output(
      ["gcloud", "config", "get-value", "project"],
      text=True,
      stderr=subprocess.PIPE
    ).strip()
    if not project_id:
      print("❌ Error: No project ID found. Please configure gcloud CLI.", file=sys.stderr)
      print("  Run 'gcloud init' or 'gcloud config set project YOUR_PROJECT_ID'.", file=sys.stderr)
      sys.exit(1)
    return project_id
  except FileNotFoundError:
    print("❌ Error: 'gcloud' command not found.", file=sys.stderr)
    print("  Please ensure the Google Cloud SDK is installed and in your PATH.", file=sys.stderr)
    sys.exit(1)
  except subprocess.CalledProcessError as e:
    print(f"❌ Error getting project ID from gcloud: {e.stderr}", file=sys.stderr)
    sys.exit(1)

def main():
  """
  Deploys the MCP Vertex AI Retail Search server to Google Cloud Run
  with internal-only access, mirroring the logic of deploy_internal.sh.
  """
  # Load environment variables from .env file
  load_dotenv()

  parser = argparse.ArgumentParser(
    description="Deploy the MCP Vertex AI Retail Search server to Google Cloud Run.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  # Core Configuration
  parser.add_argument("--project-id", default=_get_gcloud_project_id(), help="Google Cloud Project ID.")
  parser.add_argument("--region", default="us-central1", help="Google Cloud Region for Cloud Run and Artifact Registry.")
  parser.add_argument("--repository-name", default="mcp-repo", help="Artifact Registry repository name.")
  
  # Service Configuration
  parser.add_argument("--service-name", required=True, help="Name of the Cloud Run service.")
  parser.add_argument("--service-account", help="Service account to be used by the Cloud Run service.")
  
  # Network Configuration
  parser.add_argument("--network", help="VPC Network for the service.")
  parser.add_argument("--subnet", help="VPC Subnet for the service. Requires --network.")
  parser.add_argument(
    "--ingress",
    default="all",
    choices=['internal', 'all', 'internal-and-cloud-load-balancing'],
    help="Ingress control for the service."
  )
  parser.add_argument(
    "--vpc-egress",
    default="all-traffic",
    choices=['all-traffic', 'private-ranges-only'],
    help="VPC egress control."
  )
  
  # Execution Mode
  parser.add_argument("--dry-run", action="store_true", help="Print the gcloud command without executing it.")

  args = parser.parse_args()

  if args.subnet and not args.network:
    parser.error("--subnet requires --network to be specified.")

  # ==============================================================================
  # Configuration
  # ==============================================================================
  project_id = args.project_id
  region = args.region
  repository_name = args.repository_name
  service_name = args.service_name
  vpc_network = args.network
  subnet = args.subnet
  ingress = args.ingress
  vpc_egress = args.vpc_egress

  # --- Application Environment Variables ---
  # Load from .env file or use default values
  app_project_id = project_id
  app_location = os.getenv("APP_LOCATION", "global")
  app_catalog_id = os.getenv("APP_CATALOG_ID", "default_catalog")
  app_serving_config_id = os.getenv("APP_SERVING_CONFIG_ID", "default_search")

  # ==============================================================================
  # Script Logic
  # ==============================================================================

  # --- Derived Variables ---
  image_name = f"{region}-docker.pkg.dev/{project_id}/{repository_name}/mcp-vertexai-retail-search-server:latest"
  
  env_vars = {
    "PROJECT_ID": app_project_id,
    "LOCATION": app_location,
    "CATALOG_ID": app_catalog_id,
    "SERVING_CONFIG_ID": app_serving_config_id,
  }
  env_vars_string = ",".join([f"{k}={v}" for k, v in env_vars.items()])

  print(f"🚀 Starting deployment of '{service_name}' to Cloud Run...")
  print("--------------------------------------------------")
  print(f"  Project:         {project_id}")
  print(f"  Region:          {region}")
  print(f"  Service:         {service_name}")
  if args.service_account:
    print(f"  Service Account: {args.service_account}")
  print(f"  Image:           {image_name}")
  if vpc_network:
    print(f"  Network:         {vpc_network}")
  if subnet:
    print(f"  Subnet:          {subnet}")
  print(f"  Ingress:         {ingress}")
  print(f"  VPC Egress:      {vpc_egress}")
  print("  App Env Vars:")
  print(f"    LOCATION:          {app_location}")
  print(f"    CATALOG_ID:        {app_catalog_id}")
  print(f"    SERVING_CONFIG_ID: {app_serving_config_id}")
  print("--------------------------------------------------")
  print()

  # --- Deployment Command ---
  gcloud_command = [
    "gcloud", "run", "deploy", service_name,
    "--image", image_name,
    "--region", region,
    "--ingress", ingress,
    "--vpc-egress", vpc_egress,
    f"--set-env-vars={env_vars_string}",
    "--allow-unauthenticated",
  ]

  if vpc_network:
    gcloud_command.extend(["--network", vpc_network])
  
  if subnet:
    gcloud_command.extend(["--subnet", subnet])

  if args.service_account:
    gcloud_command.extend(["--service-account", args.service_account])

  if args.dry_run:
    print("DRY RUN: The following command would be executed:\n")
    # Format the command for better readability
    print(" ".join(gcloud_command))
    print()
    sys.exit(0)

  try:
    # Using subprocess.run to execute the command
    # set check=True to raise an exception on non-zero exit codes (like 'set -e')
    process = subprocess.run(
      gcloud_command,
      check=True,
      text=True,
      stdout=sys.stdout,
      stderr=sys.stderr
    )
    print()
    print("✅ Deployment script finished.")
    print(f"Service '{service_name}' has been deployed successfully.")

  except FileNotFoundError:
    print("❌ Error: 'gcloud' command not found.", file=sys.stderr)
    print("  Please ensure the Google Cloud SDK is installed and in your PATH.", file=sys.stderr)
    sys.exit(1)
  except subprocess.CalledProcessError:
    # The error message from gcloud will be printed directly to stderr
    print("\n❌ Deployment failed. Please check the error message above.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
  main()