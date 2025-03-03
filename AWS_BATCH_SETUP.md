# AWS Batch Setup Guide (GPU Configuration)

This guide walks through setting up AWS Batch for GPU-accelerated YOLO Dog Detection service.

## Prerequisites

- Docker image already pushed to ECR (with NVIDIA base image)
- IAM permissions to create AWS Batch resources
- S3 bucket already created

## 1. Create IAM Roles

### 1.1 Create ECS Task Role

This role allows your container to access AWS services

1. Go to IAM Console
2. Click "Roles" → "Create role"
3. Select "AWS service" and "Elastic Container Service Task"
4. Add these policies:
   - `AmazonS3FullAccess` (or your custom S3 policy)
5. Name it `YoloDetectionTaskRole`

### 1.2 Create EC2 Instance Role

This role allows EC2 instances to access required services

1. Go to IAM Console
2. Click "Roles" → "Create role"
3. Select "AWS service" and "EC2"
4. Add these policies:
   - `AmazonEC2ContainerServiceforEC2Role`
   - `AmazonEC2ContainerRegistryReadOnly`
   - `AmazonS3FullAccess` (or your custom S3 policy)
5. Name it `YoloDetectionEC2Role`

### 1.3 Create Service Role for AWS Batch

This role allows Batch to call AWS services

1. Go to IAM Console
2. Click "Roles" → "Create role"
3. Select "AWS service" and "Batch"
4. Add these policies:
   - `AWSBatchServiceRole`
5. Name it `AWSBatchServiceRole`

## 2. Network Configuration

### 2.1 VPC Setup

You can use the default VPC, but for production, consider creating a dedicated VPC:

1. Go to VPC Console
2. Create New:
   - Select "VPC and more"
   - Add auto-generate "your-project-name"
   - **Important**: Ensure "Enable Internet Gateway" is selected
   - **Important**: Select at least two Availability Zones
   - **CRITICAL**: Enable "Auto-assign public IPv4 address" for the subnets
   - Create VPC

3. If using existing subnets, verify/enable public IP auto-assign:
   - Go to VPC Console → Subnets
   - Select your subnet
   - Actions → Edit subnet settings
   - Check ✓ "Enable auto-assign public IPv4 address"
   - Save

### 2.2 Security Group Setup

1. Go to EC2 Console → Security Groups (left sidebar)
2. Click "Create Security Group"
3. Basic Details:

   ```
   Security group name: yolo-batch-sg
   Description: Security group for YOLO Batch GPU compute environment
   VPC: Select the VPC you just created
   ```

4. Inbound rules (click "Add rule" for each):

   ```
   # Required for SSH access (debugging)
   Type: SSH (22)
   Source: Your IP range or VPN/Bastion host IP

   # If using custom protocols/ports for your callback URLs
   Type: HTTPS (443)
   Source: 0.0.0.0/0
   ```

5. Outbound rules:

   ```
   # Default allows all outbound traffic (recommended)
   Type: All traffic
   Destination: 0.0.0.0/0
   ```

6. Click "Create security group"

## 3. Create Compute Environment

1. Go to AWS Batch Console
2. Click "Compute environments" → "Create"
3. Configure the compute environment:

   ```
   Name: YoloDetectionGPUCompute
   Type: Managed
   Provisioning Model: EC2

   Instance Types:
   - Optimal (select from p3, p4, g4dn, or g5 families)
   OR specific types:
   - g4dn.xlarge (1 GPU, 4 vCPUs, 16 GiB memory) # Most cost-effective
   - p3.2xlarge (1 GPU, 8 vCPUs, 61 GiB memory)  # Better performance

   Maximum vCPUs: 16 (adjust based on needs)

   Allocation Strategy: BEST_FIT_PROGRESSIVE
   ```

4. Network configuration:

   ```
   VPC: Select your VPC
   Subnets: Select at least two public subnets
   Security groups: Select yolo-batch-sg
   ```

5. Additional settings:

   ```
   Service role: AWSBatchServiceRole
   Instance role: YoloDetectionEC2Role
   EC2 key pair: Select or create a key pair (for debugging access)

   Launch template:
   - Select AMI: AWS Deep Learning AMI GPU CUDA 11.x (Amazon Linux 2)
     # This AMI comes with:
     # - NVIDIA drivers pre-installed
     # - nvidia-docker runtime configured
     # - CUDA toolkit
   ```

6. Click "Create compute environment"

## 4. Create Job Queue

1. In AWS Batch Console, go to "Job queues" → "Create"
2. Configure the queue:

   ```
   Name: YoloDetectionGPUQueue
   Priority: 1
   Connected compute environments: Select your YoloDetectionGPUCompute
   ```

3. Click "Create"

## 5. Create Job Definition

1. Go to "Job definitions" → "Create"
2. Configure the job definition:

   ```
   Name: yolo-detection-gpu-job
   Platform type: EC2
   Execution role/Job Role: YoloDetectionTaskRole
   ```

3. Container properties:

   ```
   Image: YOUR_ECR_IMAGE_URI
   Command: python src/main.py --video_url Ref::video_url --callback_url Ref::callback_url
   ["python","src/main.py","--video_url","Ref::video_url","--callback_url","Ref::callback_url"]

   vCPUs: 4
   Memory: 16384 MB
   GPUs: 1

   Environment variables:
   - AWS_REGION: YOUR_REGION
   - S3_BUCKET: YOUR_BUCKET
   - NVIDIA_VISIBLE_DEVICES: all
   ```

> ![NOTE]
> You may not be able to set NVIDIA_VISABLE_DEVICES:
> A container with GPU resource requirements cannot specify 'NVIDIA_VISIBLE_DEVICES' as an environment variable since this environment variable is reserved to be used in GPU workflow.

4. Linux Parameters:

- Defaults

5. Click "Create"

## 6. Test the Setup

### 6.1 Using AWS Console

1. Go to "Jobs" → "Submit new job"
2. Configure the job:

   ```
   Name: test-dog-detection-gpu
   Job definition: yolo-detection-gpu-job
   Job queue: YoloDetectionGPUQueue
   ```

3. Add parameters:

   ```json
   {
     "video_url": "https://example.com/sample.mp4",
     "callback_url": "https://your-api.com/callback"
   }
   ```

4. Click "Submit"

### 6.2 Using AWS CLI

```bash
aws batch submit-job \
    --job-name test-dog-detection-gpu \
    --job-queue YoloDetectionGPUQueue \
    --job-definition yolo-detection-gpu-job \
    --parameters video_url=https://example.com/sample.mp4,callback_url=https://d20b68c7230e.ngrok.app
```

## 7. Monitor Jobs

1. View job status in AWS Batch Console:
   - Go to "Jobs"
   - Find your job in the list
   - Click on it to see details

2. View logs in CloudWatch:
   - Jobs automatically log to CloudWatch
   - Find logs under `/aws/batch/job`

3. GPU Monitoring:
   - SSH into the EC2 instance (if needed)
   - Run `nvidia-smi` to check GPU status
   - CloudWatch metrics will include GPU utilization

## 8. Cost Management (Important for GPU)

1. Use appropriate instance types:
   - g4dn for most workloads (cheaper)
   - p3/p4 for maximum performance
   - Consider Spot instances for non-time-critical workloads

2. Instance management:
   - Set maximum vCPUs to control costs
   - Use auto-scaling to terminate idle instances
   - Monitor GPU utilization

## 9. GPU-Specific Troubleshooting

1. GPU not detected:
   - Check instance type (must be GPU-enabled)
   - Verify NVIDIA drivers installed
   - Check container runtime configuration

2. Poor GPU performance:
   - Monitor GPU utilization with `nvidia-smi`
   - Check memory usage
   - Verify batch sizes appropriate for GPU memory

3. Container errors:
   - Verify NVIDIA runtime configured
   - Check GPU device mapping
   - Validate Docker image built with CUDA support

## 10. Production Best Practices

1. GPU Optimization:
   - Match batch size to GPU memory
   - Use appropriate CUDA versions
   - Monitor GPU utilization

2. Cost Optimization:
   - Use Spot instances when possible
   - Implement proper auto-scaling
   - Monitor GPU utilization metrics

3. Performance:
   - Choose appropriate GPU instance types
   - Optimize model for inference
   - Use GPU metrics for scaling decisions

## Additional Resources

- [AWS Batch with GPU Guide](https://docs.aws.amazon.com/batch/latest/userguide/gpu-jobs.html)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [AWS GPU Instance Types](https://aws.amazon.com/ec2/instance-types/#Accelerated_Computing)
