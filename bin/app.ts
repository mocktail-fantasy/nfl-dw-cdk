import { App } from 'aws-cdk-lib';
import { DataWarehouseStack } from '../lib/dw-stack';
import { PipelineStack as CDKPipelineStack } from '../lib/cdk-pipeline-stacks';

const app = new App();

new  DataWarehouseStack(app, 'DataWarehouseStack');

new  CDKPipelineStack(app, 'CDKPipelineStack');

app.synth();
