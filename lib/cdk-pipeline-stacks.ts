import {Stack, StackProps, SecretValue} from "aws-cdk-lib";
import { Construct } from "constructs";
import * as codebuild from "aws-cdk-lib/aws-codebuild";
import * as codepipeline from "aws-cdk-lib/aws-codepipeline";
import * as codepipeline_actions from "aws-cdk-lib/aws-codepipeline-actions";
import * as iam from "aws-cdk-lib/aws-iam";

export class PipelineStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const sourceOutput = new codepipeline.Artifact();
    const cloudAssemblyOutput = new codepipeline.Artifact();

    const buildProject = new codebuild.PipelineProject(this, "CdkBuildProject", {
      projectName: "CdkPipelineBuild",
      description: "Synthesizes the CDK app",
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        privileged: false,
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: "0.2",
        phases: {
          install: {
            "runtime-versions": {
              nodejs: "20",
            },
            commands: [
              "npm install -g aws-cdk@latest",
              'npx cdk-assets publish --path dist/manifest.json',
              "npm ci",
            ],
          },
          build: {
            commands: [
              "npx cdk synth --output dist",
            ],
          },
        },
        artifacts: {
          "base-directory": "dist",
          files: "**/*",
        },
      }),
    });

    const assetPublishProject = new codebuild.PipelineProject(this, "AssetPublishProject", {
        projectName: "CdkAssetsPublish",
        description: "Publishes CDK assets (Lambda zips, Docker images) to S3/ECR",
        environment: {
          buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        },
        buildSpec: codebuild.BuildSpec.fromObject({
          version: "0.2",
          phases: {
            install: {
              commands: [
                "npm install -g aws-cdk"
              ],
            },
            build: {
              commands: [
                "npx cdk-assets publish --path manifest.json"
              ],
            },
          },
        }),
      });

    buildProject.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        "cloudformation:*",
        "s3:*",
        "iam:PassRole",
        "ec2:Describe*",
        "lambda:*",
        "logs:*",
        "sts:GetCallerIdentity",
      ],
      resources: ["*"],
    }));

    const sourceAction = new codepipeline_actions.GitHubSourceAction({
      actionName: 'GitHub_Source',
      owner: 'mocktail-fantasy',
      repo: 'nfl-dw-cdk',
      oauthToken: SecretValue.secretsManager('GitHubOAuthToken'),
      output: sourceOutput,
      branch: 'main',
    });

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: "Synth",
      project: buildProject,
      input: sourceOutput,
      outputs: [cloudAssemblyOutput],
    });

    const assetPublishAction = new codepipeline_actions.CodeBuildAction({
        actionName: 'PublishAssets',
        project: assetPublishProject,
        input: cloudAssemblyOutput,
      });
      
    const deployPipelineAction = new codepipeline_actions.CloudFormationCreateUpdateStackAction({
      actionName: "Deploy_PipelineStack",
      templatePath: cloudAssemblyOutput.atPath("CDKPipelineStack.template.json"),
      stackName: "CdkAppStack",
      adminPermissions: true,
    });

    const deployDataWarehouseAction = new codepipeline_actions.CloudFormationCreateUpdateStackAction({
        actionName: "Deploy_DataWarehouse",
        templatePath: cloudAssemblyOutput.atPath("DataWarehouseStack.template.json"),
        stackName: "DataWarehouseStack",
        adminPermissions: true,
      });

    new codepipeline.Pipeline(this, "CdkPipeline", {
      pipelineType: codepipeline.PipelineType.V2,
      pipelineName: "CdkPipeline",
      stages: [
        {
          stageName: "Source",
          actions: [sourceAction],
        },
        {
          stageName: "Build",
          actions: [buildAction],
        },
        {
          stageName: "Assets",
          actions: [assetPublishAction],
        },
        {
          stageName: "Deploy",
          actions: [deployPipelineAction, deployDataWarehouseAction],
        },
      ],
    });
  }
}
