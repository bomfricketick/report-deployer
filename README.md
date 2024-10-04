# Report Deployer

This is a simple tool to deploy reports (.pbix and .rdl) to powerbi services. It is designed to be used in a CI/CD pipeline.

It only looks for .pbix and .rdl files that is specified in the config file and deploy them to the specified workspace.



Example of config.yaml
```yaml
reports:
  - name: "report1"
    environment:
      dev:
        workspace: "dev-workspace"
        subFolder: "subfolderObjectId"
      uat:
        workspace: "test-workspace"
      prd:
        workspace: "prd-workspace"
````


Example of usage
```yaml
name: Deploy Reports Workflow

on: [push]

jobs:
  deploy-reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v45
        with:
          separator: ","
          quotepath: false
      - name: Power BI Workspace Deploy
        uses: ./.github/actions/action-a@v1.0
        with:
          files: ${{ steps.changed-files.outputs.all_modified_files }}
          env: ${{ github.event_name }}
          config_file: ".github/config/workspace-deploy-config.yaml"
        env:
          TENANT_ID: ${{ secrets.TENANT_ID }}
          CLIENT_ID: ${{ secrets.CLIENT_ID }}
          CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
````



