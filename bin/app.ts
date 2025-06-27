import { App } from 'aws-cdk-lib';
import { DataWarehouseStack } from '../lib/dw-stack';
import { PipelineStack } from '../lib/cdk-pipeline-stacks';

const app = new App();

new  DataWarehouseStack(app, 'DataWarehouseStack');

new  PipelineStack(app, 'PipelineStack');

app.synth();
