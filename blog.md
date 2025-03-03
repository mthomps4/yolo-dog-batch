# Navigating GPUs for AI in the Cloud: A Comprehensive Guide

In the world of artificial intelligence (AI), the demand for processing power has skyrocketed. While CPUs have long been the backbone of computing, GPUs (Graphics Processing Units) have emerged as the preferred choice for AI workloads. This blog will explore the advantages of using GPUs in the cloud, particularly for tasks such as AI tracking and video highlighting.

## Why GPUs?

GPUs are designed to handle multiple tasks simultaneously, making them ideal for the parallel processing required in AI applications. Unlike CPUs, which are optimized for sequential processing, GPUs can process thousands of threads at once. This capability is particularly beneficial for deep learning models, which require extensive computations on large datasets.

Given that most data science and machine learning models are developed in Python, it's important to understand a key limitation: Python's Global Interpreter Lock (GIL) means that even with multiple CPU cores, a single Python process can only execute one thread at a time. This limitation makes GPU acceleration even more crucial for AI workloads, as it allows us to bypass Python's threading constraints and leverage true parallel processing capabilities.

## AI Tracking and Highlighting Videos

While not every AI task needs a GPU, many complex computations, especially those involving large datasets or real-time processing, can significantly benefit from the parallel processing capabilities that GPUs offer. This is particularly true for tasks such as image recognition, natural language processing, and video analysis, where the speed and efficiency of GPUs can lead to faster model training and improved performance in production environments.

The use of GPUs in the cloud for AI tracking and video highlighting is a game-changer across various industries. With our clients we've seen all sorts of applications, such as monitoring patients in hospitals, physical therapy, analyzing downtown traffic patterns, and enhancing sports analytics. With the ability to process video feeds in real-time, GPUs excel at tracking movements, pinpointing significant moments, and creating engaging highlights. This capability not only boosts viewer engagement but also delivers critical insights for nurses, coaches, and players alike.

With companies like [Anthropic (Claude)](https://www.anthropic.com/news/anthropic-raises-series-e-at-usd61-5b-post-money-valuation) securing significant seed funding and open-source communities like [Hugging Face](https://huggingface.co/) continuing to grow, we are just scratching the surface of what is possible in AI development.

## Example Scenario

Let us take this sample video of two cute dogs.
[dog-video](./dog-video)
For AI to track all the dogs in the video we first need to break this video down frame by frame.
We then run those frames through an AI model for image recognition, highlight what was found, and stitch these frames back together in a new video.

Leveraging models like [Ultralytics Yolo v8](https://docs.ultralytics.com/models/yolov8/) make this a relatively easy task.
While this example demonstrates the power of AI video processing, it raises important questions about scalability and infrastructure.
How do we scale this this service to be available for millions of users?!

## Scaling Challenges

We know how this all works for one video; AI leverages our GPU for efficiency, and the model does what it was trained to do. Until recent years, our focus has primarily been on CPU usage, especially in web applications. The challenge lies in how we present our static database or Excel data to users. This represents a different type of scaling. While web apps typically prioritize the number of users connected to a single CPU thread, AI and video analytics require a more dynamic approach. They must efficiently manage vast amounts of data and processing power to deliver real-time insights and analytics. While a web app can live within a fraction of a CPU -- our new AI tasks need the machines full resources to function. As we move forward, understanding how to scale GPU resources effectively will be crucial for maximizing the potential of AI applications in various industries.

## GPUs in the cloud

For this blog we are going to primarily focus on AWS. However, these same principles will apply to Microsoft Azure, Google, etc.

Amazon Web Services (AWS) offers a variety of services that make it easy to harness the power of GPUs for AI applications:

- **EC2 (Elastic Compute Cloud)**: AWS EC2 provides instances with powerful GPU capabilities, allowing you to run your AI models efficiently. You can choose from a [range of instance types](https://docs.aws.amazon.com/dlami/latest/devguide/gpu.html) optimized for different workloads. Amazon has even started to adopt open sourced images like [Bottlerocket/Nvidia containers](https://aws.amazon.com/blogs/containers/bottlerocket-support-for-nvidia-gpus/) to build upon. While these EC2 instances can be powerful on their own. It's still only one "machine" with a limited number of GPUs. Likely great for small apps or training a new model, but we want more!
- **ECS/Fargate**: Although Fargate does not support GPUs, ECS can still be leveraged to launch EC2 instances equipped with GPU capabilities. However, the available image types are restricted to "Amazon Linux w/ GPU" and Bottlerocket GPU images. While these options may suffice, it's essential to consider them when designing your architecture and Docker builds. ECS excels in load balancing and scaling full applications, but it doesn't fully address our specific needs. We have individual requests and processes that require GPU resources, and we don't necessarily want to scale an entire application for that. In the web application context, we often think of delegating these requests to a "worker"—a separate entity that can process tasks and notify us of the results. This is where "AWS Batch" comes into play.
- **AWS Batch**: Saving the best for last. For our batch processing requirements, AWS Batch can automatically allocate the appropriate amount of compute resources, including GPU instances, to efficiently execute your AI jobs. This service is ideal for handling large datasets or conducting complex simulations. AWS Batch will establish a base Compute Resource (EC2), a Job Definition (which specifies the resources needed to complete the task—such as 1 GPU), and a queue for all incoming requests. As requests come in, AWS Batch will dynamically provision additional EC2 resources to accommodate the demand. This greatly reduces our costs we now can run our web app on a normal CPU layer and only trigger GPU instances when needed to process with our AI Models.

Referring back to our Dog video example, we used an EC2 instance with the image type `g4dn.xlarge`—the key point here is that our base Compute instance is equipped with 1 GPU. When a request is received, a new job is queued based on our job definition. This definition specifies that we require 1 GPU for the task to execute. Consequently, for each incoming request, we will quickly spin up an EC2 instance, execute our processing commands, and then terminate that instance to minimize costs. If our base EC2 Compute Environment had 4 GPUs, we could handle 4 requests before needing to scale up to a new instance. Ultimately, the decision on the size of the instance depends on your specific requirements. For most applications, particularly as an "AI worker," 1 GPU is typically sufficient for the individual tasks we aim to perform.

Mix this in with a normal web app listening for these workers response, and we users can "fire and forget" all the videos they wish to process without bogging down our users experience. Once the batch worker completes, we'll save the results for the end user to enjoy.

## Conclusion

In summary, exploring the use of GPUs in the cloud reveals immense opportunities for AI applications. While we discussed several AWS services today, these concepts are broadly applicable across various platforms. Are we optimizing the entire application? Do we require a powerful machine for model training or to handle numerous user requests? By utilizing services such as AWS EC2 and AWS Batch, you can fully harness the capabilities of your AI initiatives. Stay tuned for more insights as we explore specific use cases and best practices in upcoming blogs.

[dog final](./)
