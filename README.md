# Report Deployer

This is a simple tool to deploy reports (.pbix and .rdl) to powerbi services. It is designed to be used in a CI/CD pipeline.



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

